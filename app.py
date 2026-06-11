import streamlit as st
import requests
import json
import base64
import uuid
from datetime import datetime
from supabase import create_client

st.set_page_config(
    page_title="ARIA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SECRETS ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY   = st.secrets["GROQ_API_KEY"]
OPENROUTER_KEY = st.secrets.get("OPENROUTER_KEY", "")
COHERE_KEY     = st.secrets.get("COHERE_KEY", "")
SUPABASE_URL   = st.secrets["SUPABASE_URL"]
SUPABASE_KEY   = st.secrets["SUPABASE_KEY"]
SERPER_KEY     = st.secrets.get("SERPER_API_KEY", "")
TODAY          = datetime.now().strftime("%B %d, %Y")

# ── MODELS & MODES ─────────────────────────────────────────────────────────────
MODELS = {
    "⚡ Gemini 2.5 Pro":    "gemini-pro",
    "💨 Gemini 2.5 Flash":  "gemini-flash",
    "🚀 Groq Llama 3.3":    "groq",
    "🔥 Llama 4 Scout":     "llama4",
    "🧠 Cohere R+":         "cohere",
    "🤖 Auto Route":        "auto",
}
MODES = {
    "🤖 AI Engineering":   "ai_engineer",
    "🏗️ Zoho / ERP":        "zoho",
    "⚙️ Automation":        "automation",
    "🐍 Python Expert":    "python",
    "🌐 Web Builder":      "web",
    "💡 General":          "general",
}
MODE_ICONS = {
    "ai_engineer": "🤖", "zoho": "🏗️", "automation": "⚙️",
    "python": "🐍", "web": "🌐", "general": "💡",
}

# ── SYSTEM PROMPT ──────────────────────────────────────────────────────────────
BASE_PROMPT = f"""You are ARIA — Advanced Reasoning & Intelligence Assistant.
You are Sri's (Srimani26) exclusive personal AI. Sri is an AI Engineer & Automation Engineer at Standard Roofs, Erode, Tamil Nadu, India.

## Sri's context
- Building Roofing ERP SaaS on Zoho One for Indian roofing companies
- Zoho CRM Deluge: calculateRoofAreas (multi-section, slope/extension logic)
- Sri AI Memory MCP server — FastAPI + MCP (live on Render)
- Google Ads AI Advisor, ARIA AI Agent (Streamlit + multi-model)
- Frontend: HTML, CSS, JS, React | Backend: FastAPI, async, Pydantic
- Tools: n8n, Make.com, LangChain, Supabase, ChromaDB
- Portfolio: srimani26.github.io | GitHub: Srimani26

## Response style
- Step-by-step for complex problems
- Complete, production-ready, commented code — never partial snippets
- Diagnose root cause on errors — don't just patch symptoms
- Direct, confident, no fluff — treat Sri as a senior peer
- Always consider Indian market context
- Today: {TODAY}

## Personality
Senior engineer + trusted advisor. Honest, precise, encouraging.
Sri is ~3.5 years into his career building real products."""

MODE_EXTRAS = {
    "ai_engineer": "\nMODE: AI Engineering — LLMs, RAG, agents, MCP, embeddings, LangChain, vector DBs.",
    "zoho":        "\nMODE: Zoho/ERP — Zoho One, Deluge scripting, CRM customization, roofing ERP, Indian SMB.",
    "automation":  "\nMODE: Automation — n8n, Make.com, Python bots, API integrations, webhooks.",
    "python":      "\nMODE: Python Expert — FastAPI, async/await, Pydantic, OOP, clean architecture.",
    "web":         "\nMODE: Web Builder — complete HTML/CSS/JS or React, responsive, polished.",
    "general":     "\nMODE: General — well-rounded assistant, practical advice.",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, section.main {
    background: #080810 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: #e2e2f0 !important;
}
.block-container {
    max-width: 820px !important;
    padding: 0 20px 140px !important;
    margin: 0 auto !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0c0c1a !important;
    border-right: 1px solid #18182e !important;
}
[data-testid="stSidebar"] > div:first-child { background: #0c0c1a !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #a0a0c0 !important; font-family: 'Inter', sans-serif !important; }

/* ── SIDEBAR SELECTBOX ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #13132a !important;
    border: 1px solid #22223a !important;
    border-radius: 10px !important;
    color: #c8c8e8 !important;
    min-height: 40px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color: #7c6ef7 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #c8c8e8 !important; }

/* ── DROPDOWN LIST ── */
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"] {
    background: #13132a !important; border: 1px solid #22223a !important;
    border-radius: 12px !important; box-shadow: 0 12px 40px rgba(0,0,0,0.6) !important;
}
li[role="option"] {
    background: #13132a !important; color: #c8c8e8 !important;
    font-size: 13px !important; padding: 10px 14px !important;
    font-family: 'Inter', sans-serif !important;
}
li[role="option"]:hover, li[aria-selected="true"] {
    background: #1e1e38 !important; color: #a89bff !important;
}

/* ── SIDEBAR BUTTONS ── */
[data-testid="stSidebar"] button {
    background: #13132a !important; border: 1px solid #1e1e38 !important;
    border-radius: 10px !important; color: #6868a0 !important;
    font-size: 12px !important; font-family: 'Inter', sans-serif !important;
    text-align: left !important; padding: 8px 12px !important;
    margin-bottom: 2px !important; transition: all 0.15s !important;
    width: 100% !important;
}
[data-testid="stSidebar"] button:hover {
    border-color: #7c6ef7 !important; color: #a89bff !important;
    background: #1a1a32 !important;
}

/* ── TOGGLE ── */
[data-testid="stToggle"] label { color: #6868a0 !important; font-size: 12px !important; }

/* ── CHAT INPUT AREA ── */
[data-testid="stBottom"] {
    background: transparent !important; border: none !important;
    padding-bottom: 0 !important;
}
/* Gradient fade behind input */
[data-testid="stBottom"]::before {
    content: '';
    position: fixed; bottom: 0; left: 0; right: 0; height: 120px;
    background: linear-gradient(to top, #080810 55%, transparent);
    pointer-events: none; z-index: 0;
}
[data-testid="stChatInputContainer"] {
    background: #13132a !important; border: 1.5px solid #22223a !important;
    border-radius: 16px !important; overflow: hidden !important; position: relative; z-index: 1;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #7c6ef7 !important;
    box-shadow: 0 0 0 3px rgba(124,110,247,0.18) !important;
}
[data-testid="stChatInputContainer"] textarea {
    background: #13132a !important; color: #e2e2f0 !important;
    font-family: 'Inter', sans-serif !important; font-size: 14px !important;
    caret-color: #a89bff !important; border: none !important; outline: none !important;
    padding: 14px 16px !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: #33335a !important; }
[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #7c6ef7, #a855f7) !important;
    border: none !important; border-radius: 10px !important;
    color: white !important; margin: 6px !important;
}
[data-testid="stChatInputContainer"] button:hover { opacity: 0.85 !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #0e0e20 !important; border: 1px dashed #22223a !important;
    border-radius: 12px !important; padding: 8px !important;
}
[data-testid="stFileUploader"] label { color: #6060a0 !important; font-size: 12px !important; }
[data-testid="stFileUploader"] button {
    background: #13132a !important; border: 1px solid #22223a !important;
    border-radius: 8px !important; color: #8080c0 !important;
    font-size: 12px !important; padding: 6px 14px !important;
}
[data-testid="stFileUploader"] p { color: #44446a !important; font-size: 11px !important; }

/* ── SPINNER ── */
[data-testid="stSpinner"] > div { border-top-color: #7c6ef7 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #22223a; border-radius: 3px; }

/* ── ANIMATIONS ── */
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.25} }
@keyframes fadein { from{opacity:0;transform:translateY(5px)} to{opacity:1;transform:none} }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_sb():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_msg(sid, role, content, title=None):
    try:
        row = {"session_id": sid, "role": role, "content": content,
               "created_at": datetime.utcnow().isoformat()}
        if title: row["title"] = title
        get_sb().table("conversations").insert(row).execute()
    except: pass

def load_sessions(limit=15):
    try:
        r = get_sb().table("conversations").select("session_id,content,created_at") \
            .eq("role", "user").order("created_at", desc=True).limit(80).execute()
        seen = {}
        for row in r.data:
            s = row["session_id"]
            if s not in seen:
                preview = row["content"][:45] + "…" if len(row["content"]) > 45 else row["content"]
                ts = row["created_at"][:10]
                seen[s] = {"id": s, "preview": preview, "date": ts}
        return list(seen.values())[:limit]
    except: return []

def load_history(sid):
    try:
        r = get_sb().table("conversations").select("role,content") \
            .eq("session_id", sid).order("created_at").execute()
        return [{"role": x["role"], "content": x["content"]} for x in r.data]
    except: return []

def delete_session(sid):
    try:
        get_sb().table("conversations").delete().eq("session_id", sid).execute()
    except: pass

# ── WEB SEARCH ─────────────────────────────────────────────────────────────────
def web_search(q):
    if not SERPER_KEY: return ""
    try:
        r = requests.post("https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": q, "num": 5}, timeout=8)
        items = r.json().get("organic", [])[:5]
        return "\n".join(f"- {i.get('title','')}: {i.get('snippet','')}" for i in items)
    except: return ""

def needs_search(msg):
    kw = ["latest","current","today","now","recent","news","2025","2026",
          "update","price","trending","just released","what is happening"]
    return any(k in msg.lower() for k in kw)

# ── AUTO ROUTER ────────────────────────────────────────────────────────────────
def auto_route(prompt):
    p = prompt.lower()
    if any(w in p for w in ["quick","short","simple","what is","who is","when","where","how many"]):
        return "groq"
    if any(w in p for w in ["analyse","analyze","compare","strategy","business","market","plan"]):
        return "cohere" if COHERE_KEY else "gemini-pro"
    return "gemini-pro"

# ── MODEL CALLS ────────────────────────────────────────────────────────────────
def gemini_stream(messages, system, model="gemini-2.5-pro-preview-06-05", image_b64=None, image_mime=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse"
    contents = []
    for m in messages[:-1]:
        contents.append({"role": "user" if m["role"] == "user" else "model",
                          "parts": [{"text": m["content"]}]})
    # Last message — may include image
    last_parts = []
    if image_b64 and image_mime:
        last_parts.append({"inline_data": {"mime_type": image_mime, "data": image_b64}})
    last_parts.append({"text": messages[-1]["content"]})
    contents.append({"role": "user", "parts": last_parts})

    cfg = {"temperature": 0.7, "maxOutputTokens": 8192}
    if "pro" in model: cfg["thinkingConfig"] = {"thinkingBudget": 4000}
    payload = {"system_instruction": {"parts": [{"text": system}]},
               "contents": contents, "generationConfig": cfg}
    try:
        r = requests.post(url, json=payload, stream=True, timeout=90)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: "):
                    try:
                        d = json.loads(s[6:])
                        for part in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                            t = part.get("text", "")
                            if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ Gemini error: {e}"

def groq_stream(messages, system):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    msgs = [{"role": "system", "content": system}] + \
           [{"role": m["role"], "content": m["content"]} for m in messages]
    payload = {"model": "llama-3.3-70b-versatile", "messages": msgs,
               "max_tokens": 8192, "temperature": 0.7, "stream": True}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers=headers, json=payload, stream=True, timeout=60)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: ") and s != "data: [DONE]":
                    try:
                        t = json.loads(s[6:])["choices"][0].get("delta", {}).get("content", "")
                        if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ Groq error: {e}"

def openrouter_stream(messages, system, model="meta-llama/llama-4-scout"):
    if not OPENROUTER_KEY:
        yield from groq_stream(messages, system); return
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json",
               "HTTP-Referer": "https://aria-sri.streamlit.app", "X-Title": "ARIA"}
    msgs = [{"role": "system", "content": system}] + \
           [{"role": m["role"], "content": m["content"]} for m in messages]
    payload = {"model": model, "messages": msgs, "max_tokens": 8192, "temperature": 0.7, "stream": True}
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers=headers, json=payload, stream=True, timeout=90)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: ") and s != "data: [DONE]":
                    try:
                        t = json.loads(s[6:])["choices"][0].get("delta", {}).get("content", "")
                        if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ OpenRouter error: {e}"

def cohere_stream(messages, system):
    if not COHERE_KEY:
        yield from gemini_stream(messages, system); return
    headers = {"Authorization": f"Bearer {COHERE_KEY}", "Content-Type": "application/json"}
    history = [{"role": "USER" if m["role"] == "user" else "CHATBOT", "message": m["content"]}
               for m in messages[:-1]]
    payload = {"model": "command-r-plus", "message": messages[-1]["content"],
               "chat_history": history, "preamble": system, "stream": True, "max_tokens": 4096}
    try:
        r = requests.post("https://api.cohere.ai/v1/chat", headers=headers,
                          json=payload, stream=True, timeout=60)
        for line in r.iter_lines():
            if line:
                try:
                    d = json.loads(line.decode("utf-8"))
                    if d.get("event_type") == "text-generation":
                        t = d.get("text", "")
                        if t: yield t
                except: continue
    except Exception as e:
        yield f"\n\n⚠️ Cohere error: {e}"

def respond(messages, system, model, prompt="", image_b64=None, image_mime=None):
    actual = auto_route(prompt) if model == "auto" else model
    if actual == "gemini-pro":
        gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05", image_b64, image_mime)
    elif actual == "gemini-flash":
        gen = gemini_stream(messages, system, "gemini-2.5-flash", image_b64, image_mime)
    elif actual == "groq":
        gen = groq_stream(messages, system)
    elif actual == "llama4":
        gen = openrouter_stream(messages, system)
    elif actual == "cohere":
        gen = cohere_stream(messages, system)
    else:
        gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05", image_b64, image_mime)

    full = ""
    failed = False
    for chunk in gen:
        if "⚠️" in chunk: failed = True
        full += chunk
        yield chunk
    if failed:
        yield "\n\n🔄 **Switching to backup (Groq)...**\n\n"
        for chunk in groq_stream(messages, system):
            yield chunk

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "sid"      not in st.session_state: st.session_state.sid      = str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state.messages = []
if "model"    not in st.session_state: st.session_state.model    = "gemini-pro"
if "mode"     not in st.session_state: st.session_state.mode     = "general"
if "wsearch"  not in st.session_state: st.session_state.wsearch  = bool(SERPER_KEY)
if "sessions" not in st.session_state: st.session_state.sessions = None

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Header
    st.markdown("""
    <div style="padding:18px 6px 18px;border-bottom:1px solid #18182e;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:12px">
        <div style="width:38px;height:38px;border-radius:11px;flex-shrink:0;
             background:linear-gradient(135deg,#7c6ef7,#ec4899);
             display:flex;align-items:center;justify-content:center;
             font-size:17px;font-weight:800;color:#fff;letter-spacing:-1px;
             box-shadow:0 4px 20px rgba(124,110,247,.4)">A</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#e2e2f0;letter-spacing:-.3px">ARIA v3</div>
          <div style="font-size:11px;color:#33335a;margin-top:1px">Sri's Personal AI</div>
        </div>
      </div>
      <div style="display:inline-flex;align-items:center;gap:6px;margin-top:13px;
           background:#071510;border:1px solid #0a3828;color:#34d399;
           padding:4px 12px;border-radius:20px;font-size:11px;font-weight:500;letter-spacing:.02em">
        <span style="width:5px;height:5px;border-radius:50%;background:#34d399;
              animation:pulse 2s infinite;display:inline-block"></span>
        Online &amp; Ready
      </div>
    </div>
    <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}</style>
    """, unsafe_allow_html=True)

    # Model selector
    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#2a2a50;text-transform:uppercase;margin:0 0 6px">Model</p>', unsafe_allow_html=True)
    ml = st.selectbox("_m", list(MODELS.keys()), label_visibility="collapsed")
    st.session_state.model = MODELS[ml]

    # Mode selector
    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#2a2a50;text-transform:uppercase;margin:14px 0 6px">Mode</p>', unsafe_allow_html=True)
    mo = st.selectbox("_mo", list(MODES.keys()), label_visibility="collapsed")
    st.session_state.mode = MODES[mo]

    # Web search toggle
    if SERPER_KEY:
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#2a2a50;text-transform:uppercase;margin:14px 0 4px">Features</p>', unsafe_allow_html=True)
        st.session_state.wsearch = st.toggle("🌐 Web Search", value=st.session_state.wsearch)

    st.markdown('<div style="height:1px;background:#13132a;margin:14px 0"></div>', unsafe_allow_html=True)

    # New chat
    if st.button("✦  New Chat", use_container_width=True):
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.sessions = None
        st.rerun()

    # Chat history
    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#2a2a50;text-transform:uppercase;margin:14px 0 8px">Recent Chats</p>', unsafe_allow_html=True)

    if st.session_state.sessions is None:
        st.session_state.sessions = load_sessions()

    if st.session_state.sessions:
        for s in st.session_state.sessions:
            is_active = s["id"] == st.session_state.sid
            col_a, col_b = st.columns([0.82, 0.18])
            with col_a:
                btn_style = "border-color:#7c6ef7 !important;color:#a89bff !important;" if is_active else ""
                if st.button(f"{'▶ ' if is_active else ''}{s['preview']}", key=f"s_{s['id']}", use_container_width=True):
                    if not is_active:
                        st.session_state.sid = s["id"]
                        st.session_state.messages = load_history(s["id"])
                        st.rerun()
            with col_b:
                if not is_active:
                    if st.button("✕", key=f"del_{s['id']}"):
                        delete_session(s["id"])
                        st.session_state.sessions = load_sessions()
                        st.rerun()
    else:
        st.markdown('<p style="font-size:12px;color:#22224a;text-align:center;padding:10px 0">No chats yet</p>', unsafe_allow_html=True)

    # Status panel
    st.markdown(f"""
    <div style="margin-top:20px;padding:12px;background:#0d0d1e;border:1px solid #16162c;border-radius:12px">
      <p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#2a2a50;text-transform:uppercase;margin:0 0 10px">Active Models</p>
      <div style="font-size:11px;line-height:2;color:#44446a">
        <span style="color:#34d399">●</span> Gemini 2.5 Pro / Flash<br>
        <span style="color:#34d399">●</span> Groq Llama 3.3<br>
        <span style="color:{'#34d399' if OPENROUTER_KEY else '#22223a'}">●</span> Llama 4 Scout {'✓' if OPENROUTER_KEY else '—'}<br>
        <span style="color:{'#34d399' if COHERE_KEY else '#22223a'}">●</span> Cohere R+ {'✓' if COHERE_KEY else '—'}
      </div>
    </div>
    <p style="font-size:10px;color:#1e1e40;text-align:center;margin-top:12px">Srimani26 · {TODAY}</p>
    """, unsafe_allow_html=True)

# ── MAIN CHAT ──────────────────────────────────────────────────────────────────
import html as hl

def user_bubble(content, has_file=False):
    file_tag = '<span style="display:inline-flex;align-items:center;gap:4px;background:#1a1a38;border:1px solid #2a2a4a;border-radius:6px;padding:2px 8px;font-size:11px;color:#7070b0;margin-bottom:6px;display:block;width:fit-content">📎 File attached</span>' if has_file else ""
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;margin:14px 0 6px;animation:fadein 0.2s ease">
      <div style="max-width:78%;min-width:60px">
        {file_tag}
        <div style="background:linear-gradient(135deg,#1c1840,#201d52);
             border:1px solid #2d2870;border-radius:18px 18px 4px 18px;
             padding:12px 16px;color:#cdd2fe;font-size:14px;line-height:1.65;word-break:break-word">
          {hl.escape(content)}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def aria_avatar():
    st.markdown("""
    <div style="width:30px;height:30px;border-radius:9px;margin-top:2px;flex-shrink:0;
         background:linear-gradient(135deg,#7c6ef7,#ec4899);
         display:flex;align-items:center;justify-content:center;
         font-size:13px;font-weight:800;color:#fff">A</div>
    """, unsafe_allow_html=True)

# ── WELCOME SCREEN ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    # Build cards HTML separately to avoid f-string nesting issues
    _cards_data = [
        ("🤖", "AI Engineering",  "LLMs · RAG · Agents · MCP"),
        ("🏗️",  "Zoho ERP",        "Deluge · CRM · Workflows"),
        ("⚙️",  "Automation",      "n8n · Make · Python bots"),
        ("🐍",  "Python Expert",   "FastAPI · async · production"),
    ]
    _card_html = ""
    for _icon, _title, _desc in _cards_data:
        _card_html += (
            '<div style="background:#0c0c1e;border:1px solid #16162c;border-radius:14px;padding:16px;text-align:left">'
            '<div style="font-size:20px;margin-bottom:7px">' + _icon + '</div>'
            '<div style="font-size:13px;font-weight:600;color:#c0c0e0;margin-bottom:2px">' + _title + '</div>'
            '<div style="font-size:11px;color:#2a2a50">' + _desc + '</div>'
            '</div>'
        )

    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;'
        'justify-content:center;min-height:62vh;text-align:center;padding:40px 16px;'
        'animation:fadein 0.4s ease">'
        '<div style="width:76px;height:76px;border-radius:22px;margin:0 auto 22px;'
        'background:linear-gradient(135deg,#7c6ef7,#ec4899);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:32px;font-weight:800;color:#fff;'
        'box-shadow:0 0 70px rgba(124,110,247,.45)">A</div>'
        '<h1 style="font-size:26px;font-weight:700;margin:0 0 10px;'
        'background:linear-gradient(135deg,#a89bff,#f472b6);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'letter-spacing:-.4px">ARIA is ready, Sri.</h1>'
        '<p style="color:#2e2e58;font-size:14px;max-width:380px;line-height:1.75;margin:0 0 34px">'
        'Personal AI for AI engineering, Zoho ERP,<br>automation, and production Python.</p>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:460px;width:100%">'
        + _card_html +
        '</div></div>',
        unsafe_allow_html=True
    )

# ── RENDER HISTORY ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        user_bubble(msg["content"])
    else:
        c1, c2 = st.columns([0.055, 0.945])
        with c1: aria_avatar()
        with c2: st.markdown(msg["content"])

# ── FILE UPLOAD ────────────────────────────────────────────────────────────────
# Inject CSS to fully dark-theme the file uploader widget
st.markdown("""
<style>
/* Dark file uploader — override Streamlit's light defaults */
[data-testid="stFileUploaderDropzone"] {
    background: #0e0e1e !important;
    border: 1.5px dashed #22223a !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #7c6ef7 !important;
    background: #11112a !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: #33335a !important;
    font-size: 12px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #33335a !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #16162e !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #7070b0 !important;
    font-size: 12px !important;
    padding: 5px 14px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    border-color: #7c6ef7 !important;
    color: #a89bff !important;
}
/* Hide the default expander chrome and restyle */
[data-testid="stExpander"] {
    background: #0a0a18 !important;
    border: 1px solid #16162c !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary {
    color: #44446a !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
}
[data-testid="stExpander"] summary:hover { color: #7c6ef7 !important; }
[data-testid="stExpander"] > div > div {
    background: #0a0a18 !important;
    padding: 8px 14px 12px !important;
}
</style>
""", unsafe_allow_html=True)

with st.expander("📎 Attach file or image", expanded=False):
    uploaded = st.file_uploader(
        "drop",
        type=["png", "jpg", "jpeg", "webp", "gif", "pdf"],
        key="uploader",
        label_visibility="collapsed",
        help="Images are sent to Gemini Vision. PDFs are read and analyzed."
    )
    if uploaded:
        if uploaded.type.startswith("image/"):
            st.image(uploaded, width=260)
        else:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;'
                f'background:#0d0d20;border:1px solid #1a1a30;border-radius:8px;'
                f'font-size:12px;color:#6060a0">📄 {uploaded.name}</div>',
                unsafe_allow_html=True
            )

# ── CHAT INPUT ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask ARIA anything…"):
    sys_prompt = BASE_PROMPT + MODE_EXTRAS.get(st.session_state.mode, "")

    # Handle file attachment
    image_b64 = None
    image_mime = None
    pdf_text = ""
    has_file = False

    if "uploader" in st.session_state and st.session_state.uploader is not None:
        f = st.session_state.uploader
        has_file = True
        raw = f.read()
        if f.type.startswith("image/"):
            image_b64 = base64.b64encode(raw).decode()
            image_mime = f.type
            sys_prompt += f"\n\nThe user has attached an image ({f.name}). Analyze it as part of your response."
        elif f.type == "application/pdf":
            # Basic PDF text extraction via Gemini (send as base64)
            pdf_b64 = base64.b64encode(raw).decode()
            sys_prompt += f"\n\nThe user has attached a PDF document ({f.name}). It will be provided as base64. Extract and analyze its content."
            image_b64 = pdf_b64
            image_mime = "application/pdf"

    # Web search
    used_search = False
    if st.session_state.wsearch and needs_search(prompt):
        with st.spinner("🌐 Searching…"):
            results = web_search(prompt)
        if results:
            sys_prompt += f"\n\n## Live web results\n{results}\nUse these for a current, accurate answer."
            used_search = True

    if used_search:
        st.markdown('<div style="margin:4px 0 10px;display:inline-flex;align-items:center;gap:5px;background:#140e00;border:1px solid #5c3300;color:#f59e0b;padding:3px 12px;border-radius:20px;font-size:11px">🌐 Web searched</div>', unsafe_allow_html=True)

    # Render user bubble
    user_bubble(prompt, has_file=has_file)
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_msg(st.session_state.sid, "user", prompt)

    # Reset sessions cache so sidebar refreshes
    st.session_state.sessions = None

    # Render ARIA response
    c1, c2 = st.columns([0.055, 0.945])
    with c1: aria_avatar()
    with c2:
        placeholder = st.empty()
        full = ""
        api_msgs = st.session_state.messages[-22:]
        for chunk in respond(api_msgs, sys_prompt, st.session_state.model,
                             prompt, image_b64, image_mime):
            full += chunk
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

    st.session_state.messages.append({"role": "assistant", "content": full})
    save_msg(st.session_state.sid, "assistant", full)

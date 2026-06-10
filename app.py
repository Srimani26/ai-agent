import streamlit as st
import requests
import json
from datetime import datetime
import uuid
from supabase import create_client

st.set_page_config(
    page_title="ARIA — Sri's AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SECRETS ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY    = st.secrets["GEMINI_API_KEY"]
GROQ_API_KEY      = st.secrets["GROQ_API_KEY"]
OPENROUTER_KEY    = st.secrets.get("OPENROUTER_KEY", "")
COHERE_KEY        = st.secrets.get("COHERE_KEY", "")
SUPABASE_URL      = st.secrets["SUPABASE_URL"]
SUPABASE_KEY      = st.secrets["SUPABASE_KEY"]
SERPER_API_KEY    = st.secrets.get("SERPER_API_KEY", "")
TODAY             = datetime.now().strftime("%B %d, %Y")

# ── MODELS ────────────────────────────────────────────────────────────────────
MODELS = {
    "⚡ Gemini 2.5 Pro  —  Best":        "gemini-pro",
    "🔥 Llama 4 Scout  —  Powerful":     "llama4",
    "🚀 Groq Llama 3.3  —  Fastest":     "groq",
    "🧠 Cohere Command R+  —  Analysis": "cohere",
    "💨 Gemini 2.5 Flash  —  Light":     "gemini-flash",
    "🤖 Auto  —  Smart routing":         "auto",
}
MODES = {
    "🤖  AI Engineering":  "ai_engineer",
    "🏗️  Zoho / ERP":       "zoho",
    "⚙️  Automation":       "automation",
    "🐍  Python Expert":    "python",
    "🌐  Web Builder":      "web",
    "💡  General":          "general",
}

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
BASE = f"""You are ARIA — Advanced Reasoning & Intelligence Assistant.
You are Sri's (Srimani26) exclusive personal AI. Sri is an AI Engineer & Automation Engineer at Standard Roofs, Erode, Tamil Nadu, India.

## Sri's full context
- Building Roofing ERP SaaS on Zoho One for Indian roofing companies
- ERP tiers: Starter / Growth / Business (bundled Zoho One licenses + custom ERP)
- Zoho CRM custom Deluge function: calculateRoofAreas (multi-section, slope/extension logic)
- Sri AI Memory MCP server — FastAPI + MCP (live on Render)
- Google Ads AI Advisor project
- ARIA AI Agent (this app — Streamlit + multi-model)
- Frontend: HTML, CSS, JS, React | Python: FastAPI, async, Pydantic, OOP
- Tools: n8n, Make.com, LangChain, Supabase, ChromaDB
- Portfolio: srimani26.github.io | GitHub: Srimani26

## How you respond
- Think step by step for complex problems
- Always give complete, production-ready, commented code — never partial
- Diagnose root cause on errors — don't just patch symptoms
- Direct and confident — no corporate fluff
- Business context: always consider Indian market
- Today: {TODAY}

## Personality
Senior engineer + trusted advisor. Honest, precise, encouraging.
Sri is 3.5 years into his career building real products — support that ambition."""

MODE_EXTRAS = {{
    "ai_engineer": "\nMODE: AI Engineering — LLMs, RAG, agents, MCP, embeddings, LangChain, vector DBs. Deep technical answers with working code.",
    "zoho":        "\nMODE: Zoho/ERP — Zoho One, Deluge scripting, CRM customization, roofing ERP, Indian SMB market.",
    "automation":  "\nMODE: Automation — n8n, Make.com, Python bots, API integrations, webhooks.",
    "python":      "\nMODE: Python Expert — FastAPI, async/await, Pydantic, OOP, clean architecture.",
    "web":         "\nMODE: Web Builder — complete HTML/CSS/JS or React code, responsive, professional.",
    "general":     "\nMODE: General — well-rounded assistant, practical advice.",
}}

# ── SUPABASE ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_sb():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_msg(sid, role, content):
    try:
        get_sb().table("conversations").insert({{
            "session_id": sid, "role": role, "content": content,
            "created_at": datetime.utcnow().isoformat()
        }}).execute()
    except: pass

def load_sessions():
    try:
        r = get_sb().table("conversations").select("session_id,content,created_at")\
            .eq("role","user").order("created_at",desc=True).limit(60).execute()
        seen = {{}}
        for row in r.data:
            s = row["session_id"]
            if s not in seen:
                p = row["content"][:40]+"…" if len(row["content"])>40 else row["content"]
                seen[s] = {{"id":s,"preview":p}}
        return list(seen.values())[:10]
    except: return []

def load_history(sid):
    try:
        r = get_sb().table("conversations").select("role,content")\
            .eq("session_id",sid).order("created_at").execute()
        return [{{"role":x["role"],"content":x["content"]}} for x in r.data]
    except: return []

# ── WEB SEARCH ────────────────────────────────────────────────────────────────
def web_search(q):
    if not SERPER_API_KEY: return ""
    try:
        r = requests.post("https://google.serper.dev/search",
            headers={{"X-API-KEY":SERPER_API_KEY,"Content-Type":"application/json"}},
            json={{"q":q,"num":4}}, timeout=8)
        items = r.json().get("organic",[])[:4]
        return "\n".join(f"- {{i.get('title','')}}: {{i.get('snippet','')}}" for i in items)
    except: return ""

def needs_search(msg):
    kw = ["latest","current","today","now","recent","news","2025","2026",
          "update","price","trending","just released","what is happening"]
    return any(k in msg.lower() for k in kw)

# ── AUTO ROUTER ───────────────────────────────────────────────────────────────
def auto_route(prompt, mode):
    p = prompt.lower()
    if any(w in p for w in ["code","function","script","fastapi","python","debug","error","fix","build","write","create","implement"]):
        return "gemini-pro"
    if any(w in p for w in ["zoho","deluge","crm","erp","workflow","n8n","make.com","automate"]):
        return "gemini-pro"
    if any(w in p for w in ["quick","short","simple","what is","who is","when","where","how many"]):
        return "groq"
    if any(w in p for w in ["analyse","analyze","compare","strategy","business","market","plan","advice"]):
        return "cohere" if COHERE_KEY else "gemini-pro"
    return "gemini-pro"

# ── MODEL CALLS ───────────────────────────────────────────────────────────────
def gemini_stream(messages, system, model="gemini-2.5-pro-preview-06-05"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{{model}}:streamGenerateContent?key={{GEMINI_API_KEY}}&alt=sse"
    contents = [{{"role":"user" if m["role"]=="user" else "model","parts":[{{"text":m["content"]}}]}} for m in messages]
    cfg = {{"temperature":0.7,"maxOutputTokens":8192}}
    if "pro" in model: cfg["thinkingConfig"] = {{"thinkingBudget":5000}}
    payload = {{"system_instruction":{{"parts":[{{"text":system}}]}},"contents":contents,"generationConfig":cfg}}
    try:
        r = requests.post(url, json=payload, stream=True, timeout=90)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: "):
                    try:
                        d = json.loads(s[6:])
                        for p in d.get("candidates",[{{}}])[0].get("content",{{}}).get("parts",[]):
                            t = p.get("text","")
                            if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ Gemini error: {{e}}"

def groq_stream(messages, system):
    headers = {{"Authorization":f"Bearer {{GROQ_API_KEY}}","Content-Type":"application/json"}}
    msgs = [{{"role":"system","content":system}}] + [{{"role":m["role"],"content":m["content"]}} for m in messages]
    payload = {{"model":"llama-3.3-70b-versatile","messages":msgs,"max_tokens":8192,"temperature":0.7,"stream":True}}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
                          headers=headers, json=payload, stream=True, timeout=60)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: ") and s != "data: [DONE]":
                    try:
                        t = json.loads(s[6:])["choices"][0].get("delta",{{}}).get("content","")
                        if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ Groq error: {{e}}"

def openrouter_stream(messages, system, model="meta-llama/llama-4-scout"):
    if not OPENROUTER_KEY:
        yield from groq_stream(messages, system)
        return
    headers = {{"Authorization":f"Bearer {{OPENROUTER_KEY}}","Content-Type":"application/json",
               "HTTP-Referer":"https://aria-sri.streamlit.app","X-Title":"ARIA"}}
    msgs = [{{"role":"system","content":system}}] + [{{"role":m["role"],"content":m["content"]}} for m in messages]
    payload = {{"model":model,"messages":msgs,"max_tokens":8192,"temperature":0.7,"stream":True}}
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers=headers, json=payload, stream=True, timeout=90)
        for line in r.iter_lines():
            if line:
                s = line.decode("utf-8")
                if s.startswith("data: ") and s != "data: [DONE]":
                    try:
                        t = json.loads(s[6:])["choices"][0].get("delta",{{}}).get("content","")
                        if t: yield t
                    except: continue
    except Exception as e:
        yield f"\n\n⚠️ OpenRouter error: {{e}}"

def cohere_stream(messages, system):
    if not COHERE_KEY:
        yield from gemini_stream(messages, system)
        return
    headers = {{"Authorization":f"Bearer {{COHERE_KEY}}","Content-Type":"application/json","Accept":"application/json"}}
    chat_history = []
    for m in messages[:-1]:
        chat_history.append({{"role":"USER" if m["role"]=="user" else "CHATBOT","message":m["content"]}})
    payload = {{"model":"command-r-plus","message":messages[-1]["content"],
               "chat_history":chat_history,"preamble":system,"stream":True,"max_tokens":4096}}
    try:
        r = requests.post("https://api.cohere.ai/v1/chat",headers=headers,json=payload,stream=True,timeout=60)
        for line in r.iter_lines():
            if line:
                try:
                    d = json.loads(line.decode("utf-8"))
                    if d.get("event_type") == "text-generation":
                        t = d.get("text","")
                        if t: yield t
                except: continue
    except Exception as e:
        yield f"\n\n⚠️ Cohere error: {{e}}"

# ── SMART ROUTER ──────────────────────────────────────────────────────────────
def respond(messages, system, model, prompt=""):
    actual = auto_route(prompt, model) if model == "auto" else model
    if actual == "gemini-pro":
        gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05")
    elif actual == "gemini-flash":
        gen = gemini_stream(messages, system, "gemini-2.5-flash")
    elif actual == "groq":
        gen = groq_stream(messages, system)
    elif actual == "llama4":
        gen = openrouter_stream(messages, system)
    elif actual == "cohere":
        gen = cohere_stream(messages, system)
    else:
        gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05")

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

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* Full dark background */
html, body { background: #0a0a10 !important; }
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, section.main, .stApp {
    background: #0a0a10 !important;
    font-family: 'Inter', sans-serif !important;
}
.block-container {
    max-width: 800px !important;
    padding: 20px 24px 120px !important;
    margin: 0 auto !important;
}

/* Hide Streamlit UI */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stHeader"] {
    display: none !important;
}

/* Sidebar */
[data-testid="stSidebar"] > div:first-child {
    background: #0d0d18 !important;
    border-right: 1px solid #1a1a2e !important;
}
[data-testid="stSidebar"] { background: #0d0d18 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #c8c8e0 !important; }

/* Selectbox — force dark */
[data-baseweb="select"] { background: transparent !important; }
[data-baseweb="select"] > div {
    background: #16162a !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    color: #c8c8e0 !important;
    min-height: 42px !important;
}
[data-baseweb="select"] > div:hover { border-color: #6c5ce7 !important; }
[data-baseweb="select"] * { color: #c8c8e0 !important; background: transparent !important; }

/* Dropdown list */
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
ul[role="listbox"] {
    background: #16162a !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}
li[role="option"] {
    background: #16162a !important;
    color: #c8c8e0 !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
    font-family: 'Inter', sans-serif !important;
}
li[role="option"]:hover,
li[aria-selected="true"] {
    background: #22223a !important;
    color: #a29bfe !important;
}

/* Toggle */
[data-testid="stToggle"] > label > div { color: #8888a8 !important; font-size: 13px !important; }
[role="checkbox"][aria-checked="true"] { background: #6c5ce7 !important; }

/* Sidebar buttons */
[data-testid="stSidebar"] button {
    background: #16162a !important;
    border: 1px solid #2a2a44 !important;
    border-radius: 10px !important;
    color: #8888a8 !important;
    font-size: 12.5px !important;
    font-family: 'Inter', sans-serif !important;
    text-align: left !important;
    transition: all 0.15s !important;
    padding: 8px 14px !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] button:hover {
    border-color: #6c5ce7 !important;
    color: #a29bfe !important;
    background: #1c1c32 !important;
}

/* ── CHAT INPUT — complete override ── */
[data-testid="stBottom"] {
    background: #0a0a10 !important;
    border: none !important;
    padding-bottom: 12px !important;
}
[data-testid="stBottom"]::before {
    content: '';
    position: fixed;
    bottom: 0; left: 0; right: 0; height: 100px;
    background: linear-gradient(to top, #0a0a10 60%, transparent);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stChatInputContainer"] {
    background: #16162a !important;
    border: 1.5px solid #2a2a44 !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    position: relative;
    z-index: 1;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #6c5ce7 !important;
    box-shadow: 0 0 0 3px rgba(108,92,231,0.2) !important;
}
[data-testid="stChatInputContainer"] textarea {
    background: #16162a !important;
    color: #e0e0f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    caret-color: #a29bfe !important;
    border: none !important;
    outline: none !important;
    padding: 14px 16px !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: #44446a !important; }
[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #6c5ce7, #a855f7) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    margin: 6px !important;
    transition: opacity 0.2s !important;
}
[data-testid="stChatInputContainer"] button:hover { opacity: 0.85 !important; }

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #6c5ce7 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a44; border-radius: 3px; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
@keyframes fadein { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none} }
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
    st.markdown("""
    <div style="padding:16px 4px 20px;border-bottom:1px solid #1a1a2e;margin-bottom:16px">
      <div style="display:flex;align-items:center;gap:11px">
        <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
             background:linear-gradient(135deg,#6c5ce7,#ec4899);
             display:flex;align-items:center;justify-content:center;
             font-size:16px;font-weight:800;color:#fff">A</div>
        <div>
          <div style="font-size:15px;font-weight:700;color:#e0e0f0;letter-spacing:-0.3px;line-height:1.2">ARIA v2</div>
          <div style="font-size:11px;color:#44446a;margin-top:2px">Sri's Personal AI</div>
        </div>
      </div>
      <div style="display:inline-flex;align-items:center;gap:6px;margin-top:14px;
           background:#081a10;border:1px solid #064e30;color:#34d399;
           padding:4px 12px;border-radius:20px;font-size:11px;font-weight:500">
        <span style="width:5px;height:5px;border-radius:50%;background:#34d399;
              display:inline-block;animation:pulse 2s infinite"></span>
        Online &amp; Ready
      </div>
    </div>
    <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}</style>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#33334a;text-transform:uppercase;margin:0 0 6px">AI Model</p>', unsafe_allow_html=True)
    ml = st.selectbox("_model", list(MODELS.keys()), label_visibility="collapsed")
    st.session_state.model = MODELS[ml]

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#33334a;text-transform:uppercase;margin:14px 0 6px">Work Mode</p>', unsafe_allow_html=True)
    mo = st.selectbox("_mode", list(MODES.keys()), label_visibility="collapsed")
    st.session_state.mode = MODES[mo]

    if SERPER_API_KEY:
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#33334a;text-transform:uppercase;margin:14px 0 6px">Features</p>', unsafe_allow_html=True)
        st.session_state.wsearch = st.toggle("🌐  Web Search", value=st.session_state.wsearch)

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#33334a;text-transform:uppercase;margin:14px 0 8px">Session</p>', unsafe_allow_html=True)
    if st.button("✦  New conversation", use_container_width=True):
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    sessions = load_sessions()
    if sessions:
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#33334a;text-transform:uppercase;margin:14px 0 6px">Recent Chats</p>', unsafe_allow_html=True)
        for s in sessions[:8]:
            if s["id"] != st.session_state.sid:
                if st.button(f"↩  {s['preview']}", key=s["id"], use_container_width=True):
                    st.session_state.sid = s["id"]
                    st.session_state.messages = load_history(s["id"])
                    st.rerun()

    # Models status
    st.markdown(f"""
    <div style="margin-top:24px;padding:12px;background:#10101e;border:1px solid #1a1a2e;border-radius:10px">
      <p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#33334a;text-transform:uppercase;margin:0 0 10px">Active Models</p>
      <div style="font-size:11px;line-height:2;color:#55556a">
        <span style="color:#34d399">●</span> Gemini 2.5 Pro<br>
        <span style="color:#34d399">●</span> Groq Llama 3.3<br>
        <span style="color:{'#34d399' if OPENROUTER_KEY else '#333355'}">●</span> Llama 4 Scout {'✓' if OPENROUTER_KEY else '(add key)'}<br>
        <span style="color:{'#34d399' if COHERE_KEY else '#333355'}">●</span> Cohere R+ {'✓' if COHERE_KEY else '(add key)'}
      </div>
    </div>
    <div style="margin-top:12px;text-align:center;font-size:10.5px;color:#22223a;line-height:1.8">
      Srimani26 · {TODAY}
    </div>
    """, unsafe_allow_html=True)

# ── MAIN CHAT AREA ────────────────────────────────────────────────────────────

def render_message(role, content):
    """Render a single chat message as clean HTML"""
    import html as htmllib
    safe = htmllib.escape(content)
    # Convert markdown code blocks to styled pre
    import re
    # code blocks
    safe_content = content
    if role == "assistant":
        # Render markdown properly via st.markdown inside container
        return None  # handled differently
    else:
        return f"""
        <div style="display:flex;justify-content:flex-end;margin:8px 0;animation:fadein 0.2s ease">
          <div style="max-width:75%;background:linear-gradient(135deg,#1a1535,#1e1b4b);
               border:1px solid #2d2766;border-radius:18px 18px 4px 18px;
               padding:12px 16px;color:#c7d2fe;font-size:14px;line-height:1.65;
               font-family:'Inter',sans-serif">
            {htmllib.escape(content)}
          </div>
        </div>"""

# Welcome screen
if not st.session_state.messages:
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
         min-height:65vh;text-align:center;padding:40px 20px">

      <div style="width:72px;height:72px;border-radius:20px;margin:0 auto 24px;
           background:linear-gradient(135deg,#6c5ce7,#ec4899);
           display:flex;align-items:center;justify-content:center;
           font-size:30px;font-weight:800;color:#fff;
           box-shadow:0 0 60px rgba(108,92,231,.4)">A</div>

      <h1 style="font-size:28px;font-weight:700;margin:0 0 12px;
           background:linear-gradient(135deg,#a29bfe,#f472b6);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent;
           letter-spacing:-0.5px">ARIA is ready, Sri.</h1>

      <p style="color:#3a3a5a;font-size:14px;max-width:380px;line-height:1.7;margin:0 0 36px">
        Your personal AI — built for complex engineering,<br>Zoho ERP, automation, and coding.
      </p>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:440px;width:100%">
        {"".join(f'''<div style="background:#0f0f1e;border:1px solid #1a1a2e;border-radius:14px;
             padding:16px;text-align:left;cursor:default;transition:border-color 0.2s">
          <div style="font-size:20px;margin-bottom:8px">{icon}</div>
          <div style="font-size:13px;font-weight:600;color:#c0c0e0">{title}</div>
          <div style="font-size:11px;color:#3a3a5a;margin-top:3px">{desc}</div>
        </div>''' for icon,title,desc in [
            ("🤖","AI Engineering","LLMs · RAG · Agents · MCP"),
            ("🏗️","Zoho ERP","Deluge · CRM · Workflows"),
            ("⚙️","Automation","n8n · Make · Python bots"),
            ("🐍","Python Expert","FastAPI · async · production"),
        ])}
      </div>
    </div>
    """, unsafe_allow_html=True)

# Render existing messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        import html as hl
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin:10px 0">
          <div style="max-width:75%;background:linear-gradient(135deg,#1a1535,#1e1b4b);
               border:1px solid #2d2766;border-radius:18px 18px 4px 18px;
               padding:12px 16px;color:#c7d2fe;font-size:14px;line-height:1.65">
            {hl.escape(msg["content"])}
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ARIA message — use columns for avatar + content
        col1, col2 = st.columns([0.06, 0.94])
        with col1:
            st.markdown("""
            <div style="width:32px;height:32px;border-radius:9px;margin-top:4px;
                 background:linear-gradient(135deg,#6c5ce7,#ec4899);
                 display:flex;align-items:center;justify-content:center;
                 font-size:14px;font-weight:800;color:#fff">A</div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:#0f0f1e;border:1px solid #1a1a2e;
                 border-radius:4px 18px 18px 18px;padding:14px 18px;
                 font-size:14px;line-height:1.78;color:#ddddf0;margin-bottom:4px">
            """, unsafe_allow_html=True)
            st.markdown(msg["content"])
            st.markdown("</div>", unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask ARIA anything…"):
    sys_prompt = BASE + MODE_EXTRAS.get(st.session_state.mode, "")

    # Web search
    used_search = False
    if st.session_state.wsearch and needs_search(prompt):
        with st.spinner("🌐 Searching web…"):
            results = web_search(prompt)
        if results:
            sys_prompt += f"\n\n## Live web results\n{results}\nUse these for an accurate, current answer."
            used_search = True

    if used_search:
        st.markdown('<div style="margin:4px 0 8px;display:inline-flex;align-items:center;gap:5px;background:#1a1400;border:1px solid #713f12;color:#fbbf24;padding:3px 12px;border-radius:20px;font-size:11px">🌐 Web search used</div>', unsafe_allow_html=True)

    # Show user message
    import html as hl
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;margin:10px 0">
      <div style="max-width:75%;background:linear-gradient(135deg,#1a1535,#1e1b4b);
           border:1px solid #2d2766;border-radius:18px 18px 4px 18px;
           padding:12px 16px;color:#c7d2fe;font-size:14px;line-height:1.65">
        {hl.escape(prompt)}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role":"user","content":prompt})
    save_msg(st.session_state.sid, "user", prompt)

    # Show ARIA response
    col1, col2 = st.columns([0.06, 0.94])
    with col1:
        st.markdown("""
        <div style="width:32px;height:32px;border-radius:9px;margin-top:4px;
             background:linear-gradient(135deg,#6c5ce7,#ec4899);
             display:flex;align-items:center;justify-content:center;
             font-size:14px;font-weight:800;color:#fff">A</div>
        """, unsafe_allow_html=True)
    with col2:
        placeholder = st.empty()
        full = ""
        api_msgs = st.session_state.messages[-20:]
        for chunk in respond(api_msgs, sys_prompt, st.session_state.model, prompt):
            full += chunk
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

    st.session_state.messages.append({"role":"assistant","content":full})
    save_msg(st.session_state.sid, "assistant", full)

import streamlit as st
import requests
import json
import base64
import uuid
from datetime import datetime
from supabase import create_client

st.set_page_config(
    page_title="ARIA — Sri's AI",
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

MODELS = {
    "⚡ Gemini 2.5 Pro":   "gemini-pro",
    "💨 Gemini 2.5 Flash": "gemini-flash",
    "🚀 Groq Llama 3.3":   "groq",
    "🔥 Llama 4 Scout":    "llama4",
    "🧠 Cohere R+":        "cohere",
    "🤖 Auto Route":       "auto",
}
MODES = {
    "🤖 AI Engineering":  "ai_engineer",
    "🏗️ Zoho / ERP":      "zoho",
    "⚙️ Automation":      "automation",
    "🐍 Python Expert":   "python",
    "🌐 Web Builder":     "web",
    "💡 General":         "general",
}

BASE_PROMPT = f"""You are ARIA — Advanced Reasoning & Intelligence Assistant.
You are Sri's (Srimani26) exclusive personal AI. Sri is an AI Engineer & Automation Engineer at Standard Roofs, Erode, Tamil Nadu, India.

## Sri's context
- Building Roofing ERP SaaS on Zoho One for Indian roofing companies
- Zoho CRM Deluge: calculateRoofAreas (multi-section, slope/extension logic)
- Sri AI Memory MCP server — FastAPI + MCP (live on Render)
- Google Ads AI Advisor, ARIA AI Agent (this app)
- Frontend: HTML/CSS/JS/React | Backend: FastAPI, async, Pydantic
- Tools: n8n, Make.com, LangChain, Supabase, ChromaDB
- Portfolio: srimani26.github.io | GitHub: Srimani26

## Response style
- Step-by-step for complex problems
- Complete, production-ready, commented code
- Diagnose root cause — don't just patch symptoms
- Direct, confident, no fluff. Today: {TODAY}"""

MODE_EXTRAS = {
    "ai_engineer": "\nMODE: AI Engineering — LLMs, RAG, agents, MCP, embeddings, LangChain, vector DBs.",
    "zoho":        "\nMODE: Zoho/ERP — Zoho One, Deluge scripting, CRM customization, roofing ERP.",
    "automation":  "\nMODE: Automation — n8n, Make.com, Python bots, API integrations.",
    "python":      "\nMODE: Python Expert — FastAPI, async/await, Pydantic, OOP.",
    "web":         "\nMODE: Web Builder — complete HTML/CSS/JS or React, responsive.",
    "general":     "\nMODE: General assistant.",
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #09090f !important;
    font-family: 'Inter', sans-serif !important;
}
.block-container {
    max-width: 800px !important;
    padding: 10px 24px 160px !important;
    margin: 0 auto !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stHeader"] { display: none !important; }

/* SIDEBAR */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background: #0d0d1c !important;
    border-right: 1px solid #1c1c30 !important;
}
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #8888aa !important; }

/* SIDEBAR SELECTBOX */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #141428 !important;
    border: 1px solid #252540 !important;
    border-radius: 10px !important;
    color: #ccccee !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color: #7c6ef7 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #ccccee !important; background: transparent !important; }

/* DROPDOWN */
[data-baseweb="popover"] > div, [data-baseweb="menu"], ul[role="listbox"] {
    background: #141428 !important; border: 1px solid #252540 !important;
    border-radius: 10px !important; box-shadow: 0 8px 32px rgba(0,0,0,.6) !important;
}
li[role="option"] { background: #141428 !important; color: #ccccee !important; font-size: 13px !important; padding: 10px 14px !important; }
li[role="option"]:hover, li[aria-selected="true"] { background: #1e1e3a !important; color: #a89bff !important; }

/* SIDEBAR BUTTONS */
[data-testid="stSidebar"] button {
    background: #141428 !important; border: 1px solid #1e1e38 !important;
    border-radius: 10px !important; color: #55557a !important;
    font-size: 12px !important; padding: 8px 12px !important;
    text-align: left !important; transition: all .15s !important; width: 100% !important;
}
[data-testid="stSidebar"] button:hover { border-color: #7c6ef7 !important; color: #a89bff !important; background: #1a1a32 !important; }

/* TOGGLE */
[data-testid="stToggle"] label { color: #55557a !important; font-size: 12px !important; }

/* CHAT MESSAGES */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 6px 0 !important;
}
/* User message — push right */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] {
    display: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #1d1850, #221d5a) !important;
    border: 1px solid #312d80 !important;
    border-radius: 18px 18px 4px 18px !important;
    max-width: 76% !important;
    margin-left: auto !important;
    padding: 12px 16px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] p {
    color: #c8d0ff !important; font-size: 14px !important; line-height: 1.65 !important; margin: 0 !important;
}
/* ARIA message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #7c6ef7, #ec4899) !important;
    border-radius: 10px !important; border: none !important;
    font-size: 14px !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: transparent !important; padding: 4px 0 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] li {
    color: #dcdcf5 !important; font-size: 14px !important; line-height: 1.8 !important;
}
/* Code */
[data-testid="stChatMessage"] code {
    background: #12122a !important; color: #a89bff !important;
    border-radius: 4px !important; padding: 2px 6px !important; font-size: 13px !important;
}
[data-testid="stChatMessage"] pre {
    background: #0c0c1e !important; border: 1px solid #1e1e36 !important;
    border-radius: 10px !important; padding: 14px 16px !important;
}
[data-testid="stChatMessage"] pre code { background: transparent !important; padding: 0 !important; color: #c5c5ee !important; }

/* CHAT INPUT */
[data-testid="stBottom"] { background: #09090f !important; padding-bottom: 12px !important; }
[data-testid="stChatInputContainer"] {
    background: #141428 !important; border: 1.5px solid #252540 !important;
    border-radius: 16px !important; overflow: hidden !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #7c6ef7 !important; box-shadow: 0 0 0 3px rgba(124,110,247,.15) !important;
}
[data-testid="stChatInputContainer"] textarea {
    background: #141428 !important; color: #e0e0f8 !important;
    font-family: 'Inter', sans-serif !important; font-size: 14px !important;
    border: none !important; caret-color: #a89bff !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: #30305a !important; }
[data-testid="stChatInputContainer"] button {
    background: linear-gradient(135deg, #7c6ef7, #a855f7) !important;
    border: none !important; border-radius: 10px !important; color: #fff !important; margin: 6px !important;
}

/* FILE UPLOADER — dark */
[data-testid="stFileUploaderDropzone"] {
    background: #0e0e1e !important; border: 1.5px dashed #252540 !important; border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: #7c6ef7 !important; }
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzoneInstructions"] div { color: #33335a !important; font-size: 12px !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: #141428 !important; border: 1px solid #252540 !important;
    border-radius: 8px !important; color: #6060a0 !important; font-size: 12px !important;
}
[data-testid="stFileUploaderDropzone"] button:hover { border-color: #7c6ef7 !important; color: #a89bff !important; }
[data-testid="stFileUploadDeleteBtn"] button { width: auto !important; }

/* IMAGE in chat */
[data-testid="stChatMessage"] img { border-radius: 10px !important; max-width: 320px !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: #252540; border-radius: 3px; }

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.2} }
@keyframes fadein { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none} }
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ───────────────────────────────────────────────────────────────────
@st.cache_resource
def get_sb():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_msg(sid, role, content):
    try:
        get_sb().table("conversations").insert({
            "session_id": sid, "role": role, "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        pass  # don't crash UI on DB error

def load_sessions():
    try:
        r = get_sb().table("conversations") \
            .select("session_id,content,created_at") \
            .eq("role", "user") \
            .order("created_at", desc=True) \
            .limit(100).execute()
        seen = {}
        for row in r.data:
            s = row["session_id"]
            if s not in seen:
                p = row["content"]
                # strip file prefix if present
                if p.startswith("📎"):
                    p = p.split("—", 1)[-1].strip()
                preview = p[:44] + "…" if len(p) > 44 else p
                seen[s] = {"id": s, "preview": preview, "date": row["created_at"][:10]}
        return list(seen.values())[:15]
    except:
        return []

def load_history(sid):
    try:
        r = get_sb().table("conversations") \
            .select("role,content") \
            .eq("session_id", sid) \
            .order("created_at").execute()
        return [{"role": x["role"], "content": x["content"]} for x in r.data]
    except:
        return []

def delete_session(sid):
    try:
        get_sb().table("conversations").delete().eq("session_id", sid).execute()
    except:
        pass

# ── WEB SEARCH ─────────────────────────────────────────────────────────────────
def web_search(q):
    if not SERPER_KEY: return ""
    try:
        r = requests.post("https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": q, "num": 5}, timeout=8)
        items = r.json().get("organic", [])[:5]
        return "\n".join(f"- {i.get('title','')}: {i.get('snippet','')}" for i in items)
    except:
        return ""

def needs_search(msg):
    kw = ["latest","current","today","now","recent","news","2025","2026",
          "update","price","trending","just released"]
    return any(k in msg.lower() for k in kw)

# ── AUTO ROUTER ────────────────────────────────────────────────────────────────
def auto_route(prompt):
    p = prompt.lower()
    if any(w in p for w in ["quick","short","what is","who is","when","where","how many"]):
        return "groq"
    if any(w in p for w in ["analyse","analyze","compare","strategy","business","plan"]):
        return "cohere" if COHERE_KEY else "gemini-pro"
    return "gemini-pro"

# ── MODEL CALLS ────────────────────────────────────────────────────────────────
def gemini_stream(messages, system, model_id="gemini-2.5-flash", img_b64=None, img_mime=None):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:streamGenerateContent?key={GEMINI_API_KEY}&alt=sse"

    contents = []

    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": m["content"]}]
        })

    payload = {
        "system_instruction": {
            "parts": [{"text": system}]
        },
        "contents": contents
    }

    try:
        r = requests.post(
            url,
            json=payload,
            stream=True,
            timeout=90
        )

        if r.status_code != 200:
            yield f"Gemini API Error {r.status_code}\n{r.text}"
            return

        for line in r.iter_lines():

            if not line:
                continue

            s = line.decode("utf-8")

            if not s.startswith("data: "):
                continue

            try:
                data = json.loads(s[6:])

                candidates = data.get("candidates", [])

                if not candidates:
                    continue

                parts = candidates[0].get("content", {}).get("parts", [])

                for part in parts:
                    text = part.get("text")

                    if text:
                        yield text

            except Exception as parse_error:
                yield f"\nParse Error: {parse_error}"

    except Exception as e:
        yield f"\nGemini Error: {e}"

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

def openrouter_stream(messages, system):
    if not OPENROUTER_KEY:
        yield from groq_stream(messages, system); return
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json",
               "HTTP-Referer": "https://aria-sri.streamlit.app", "X-Title": "ARIA"}
    msgs = [{"role": "system", "content": system}] + \
           [{"role": m["role"], "content": m["content"]} for m in messages]
    payload = {"model": "meta-llama/llama-4-scout", "messages": msgs,
               "max_tokens": 8192, "temperature": 0.7, "stream": True}
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

def respond(messages, system, model, prompt="", img_b64=None, img_mime=None):
    actual = auto_route(prompt) if model == "auto" else model
    if   actual == "gemini-pro":   gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05", img_b64, img_mime)
    elif actual == "gemini-flash":  gen = gemini_stream(messages, system, "gemini-2.5-flash", img_b64, img_mime)
    elif actual == "groq":          gen = groq_stream(messages, system)
    elif actual == "llama4":        gen = openrouter_stream(messages, system)
    elif actual == "cohere":        gen = cohere_stream(messages, system)
    else:                           gen = gemini_stream(messages, system, "gemini-2.5-pro-preview-06-05", img_b64, img_mime)
    full = ""; failed = False
    for chunk in gen:
        if "⚠️" in chunk: failed = True
        full += chunk; yield chunk
    if failed:
        yield "\n\n🔄 **Switching to Groq backup...**\n\n"
        for chunk in groq_stream(messages, system): yield chunk

# ── SESSION STATE ──────────────────────────────────────────────────────────────
if "sid"      not in st.session_state: st.session_state.sid      = str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state.messages = []
if "model"    not in st.session_state: st.session_state.model    = "gemini-pro"
if "mode"     not in st.session_state: st.session_state.mode     = "general"
if "wsearch"  not in st.session_state: st.session_state.wsearch  = bool(SERPER_KEY)
if "sessions" not in st.session_state: st.session_state.sessions = None

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
uploaded = st.file_uploader(
    "📎 Attach image or PDF (optional)",
    type=["png", "jpg", "jpeg", "webp", "gif", "pdf"],
    key="uploader",
    label_visibility="visible",
    help="Images → Gemini Vision analyzes them. PDFs → content extracted and analyzed."
)
if uploaded and uploaded.type.startswith("image/"):
    st.image(uploaded, width=280)


        '<div style="padding:16px 4px 18px;border-bottom:1px solid #1c1c30;margin-bottom:14px">'
        '<div style="display:flex;align-items:center;gap:12px">'
        '<div style="width:38px;height:38px;border-radius:11px;flex-shrink:0;'
        'background:linear-gradient(135deg,#7c6ef7,#ec4899);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:17px;font-weight:800;color:#fff;'
        'box-shadow:0 4px 20px rgba(124,110,247,.4)">⚡</div>'
        '<div>'
        '<div style="font-size:15px;font-weight:700;color:#e0e0f8">ARIA v3</div>'
        '<div style="font-size:11px;color:#2a2a4a;margin-top:1px">Sri\'s Personal AI</div>'
        '</div></div>'
        '<div style="display:inline-flex;align-items:center;gap:6px;margin-top:12px;'
        'background:#071510;border:1px solid #0a3828;color:#34d399;'
        'padding:4px 12px;border-radius:20px;font-size:11px;font-weight:500">'
        '<span style="width:5px;height:5px;border-radius:50%;background:#34d399;'
        'animation:pulse 2s infinite;display:inline-block"></span>'
        'Online &amp; Ready'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#252545;text-transform:uppercase;margin:0 0 5px">Model</p>', unsafe_allow_html=True)
    ml = st.selectbox("_m", list(MODELS.keys()), label_visibility="collapsed")
    st.session_state.model = MODELS[ml]

    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#252545;text-transform:uppercase;margin:13px 0 5px">Mode</p>', unsafe_allow_html=True)
    mo = st.selectbox("_mo", list(MODES.keys()), label_visibility="collapsed")
    st.session_state.mode = MODES[mo]

    if SERPER_KEY:
        st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#252545;text-transform:uppercase;margin:13px 0 4px">Features</p>', unsafe_allow_html=True)
        st.session_state.wsearch = st.toggle("🌐 Web Search", value=st.session_state.wsearch)

    st.markdown('<div style="height:1px;background:#141428;margin:14px 0"></div>', unsafe_allow_html=True)

    if st.button("✦  New Chat", use_container_width=True):
        st.session_state.sid = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.sessions = None
        st.rerun()

    # Chat history
    st.markdown('<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#252545;text-transform:uppercase;margin:14px 0 8px">Recent Chats</p>', unsafe_allow_html=True)
    if st.session_state.sessions is None:
        st.session_state.sessions = load_sessions()

    if st.session_state.sessions:
        for s in st.session_state.sessions:
            active = s["id"] == st.session_state.sid
            ca, cb = st.columns([0.82, 0.18])
            with ca:
                label = ("▶ " if active else "") + s["preview"]
                if st.button(label, key=f"s_{s['id']}", use_container_width=True):
                    if not active:
                        st.session_state.sid = s["id"]
                        st.session_state.messages = load_history(s["id"])
                        st.rerun()
            with cb:
                if not active:
                    if st.button("✕", key=f"d_{s['id']}"):
                        delete_session(s["id"])
                        st.session_state.sessions = load_sessions()
                        st.rerun()
    else:
        st.markdown('<p style="font-size:12px;color:#1e1e38;text-align:center;padding:8px 0">No chats yet</p>', unsafe_allow_html=True)

    # Status
    st.markdown(
        f'<div style="margin-top:20px;padding:12px;background:#0d0d1c;border:1px solid #181830;border-radius:12px">'
        f'<p style="font-size:10px;font-weight:600;letter-spacing:.1em;color:#252545;text-transform:uppercase;margin:0 0 8px">Active Models</p>'
        f'<div style="font-size:11px;line-height:2;color:#33335a">'
        f'<span style="color:#34d399">●</span> Gemini 2.5 Pro / Flash<br>'
        f'<span style="color:#34d399">●</span> Groq Llama 3.3<br>'
        f'<span style="color:{"#34d399" if OPENROUTER_KEY else "#1e1e38"}">●</span> Llama 4 Scout {"✓" if OPENROUTER_KEY else "—"}<br>'
        f'<span style="color:{"#34d399" if COHERE_KEY else "#1e1e38"}">●</span> Cohere R+ {"✓" if COHERE_KEY else "—"}'
        f'</div></div>'
        f'<p style="font-size:10px;color:#1a1a38;text-align:center;margin-top:12px">Srimani26 · {TODAY}</p>',
        unsafe_allow_html=True
    )

# ── WELCOME SCREEN ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    cards = [
        ("🤖", "AI Engineering",  "LLMs · RAG · Agents · MCP"),
        ("🏗️",  "Zoho ERP",        "Deluge · CRM · Workflows"),
        ("⚙️",  "Automation",      "n8n · Make · Python bots"),
        ("🐍",  "Python Expert",   "FastAPI · async · production"),
    ]
    cards_html = "".join(
        '<div style="background:#0d0d1e;border:1px solid #181830;border-radius:14px;padding:16px;text-align:left">'
        f'<div style="font-size:22px;margin-bottom:8px">{icon}</div>'
        f'<div style="font-size:13px;font-weight:600;color:#b8b8e0;margin-bottom:3px">{title}</div>'
        f'<div style="font-size:11px;color:#252548">{desc}</div>'
        '</div>'
        for icon, title, desc in cards
    )
    st.markdown(
        '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;'
        'min-height:60vh;text-align:center;padding:40px 16px">'
        '<div style="width:78px;height:78px;border-radius:22px;margin:0 auto 24px;'
        'background:linear-gradient(135deg,#7c6ef7,#ec4899);'
        'display:flex;align-items:center;justify-content:center;'
        'font-size:34px;color:#fff;box-shadow:0 0 80px rgba(124,110,247,.5)">⚡</div>'
        '<h1 style="font-size:27px;font-weight:700;margin:0 0 10px;'
        'background:linear-gradient(135deg,#a89bff,#f472b6);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'letter-spacing:-.4px">ARIA is ready, Sri.</h1>'
        '<p style="color:#252548;font-size:14px;max-width:360px;line-height:1.8;margin:0 0 36px">'
        'Personal AI for AI engineering, Zoho ERP,<br>automation, and production Python.</p>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:460px;width:100%">'
        + cards_html +
        '</div></div>',
        unsafe_allow_html=True
    )

# ── RENDER HISTORY ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# ── FILE UPLOADER ──────────────────────────────────────────────────────────────

# ── CHAT INPUT ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask ARIA anything…"):
    sys_prompt = BASE_PROMPT + MODE_EXTRAS.get(st.session_state.mode, "")

    # File processing
    img_b64 = None; img_mime = None; has_file = False
    if uploaded is not None:
        has_file = True
        raw = uploaded.read()
        if uploaded.type.startswith("image/"):
            img_b64 = base64.b64encode(raw).decode()
            img_mime = uploaded.type
            sys_prompt += f"\n\nUser attached image: {uploaded.name}. Analyze it as part of your answer."
        elif uploaded.type == "application/pdf":
            img_b64 = base64.b64encode(raw).decode()
            img_mime = "application/pdf"
            sys_prompt += f"\n\nUser attached PDF: {uploaded.name}. Read and analyze its content."

    # Web search
    if st.session_state.wsearch and needs_search(prompt):
        with st.spinner("🌐 Searching web…"):
            results = web_search(prompt)
        if results:
            sys_prompt += f"\n\n## Live search results\n{results}\nUse for current, accurate answer."
            st.toast("🌐 Web search used", icon="🔍")

    # Display + save user message
    display_prompt = ("📎 *[File attached]* — " if has_file else "") + prompt
    with st.chat_message("user", avatar="👤"):
        st.markdown(display_prompt)
    st.session_state.messages.append({"role": "user", "content": display_prompt})
    save_msg(st.session_state.sid, "user", display_prompt)
    st.session_state.sessions = None  # refresh sidebar

    # Stream ARIA response
    with st.chat_message("assistant", avatar="⚡"):
        placeholder = st.empty()
        full = ""
        for chunk in respond(st.session_state.messages[-22:], sys_prompt,
                             st.session_state.model, prompt, img_b64, img_mime):
            full += chunk
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

    st.session_state.messages.append({"role": "assistant", "content": full})
    save_msg(st.session_state.sid, "assistant", full)

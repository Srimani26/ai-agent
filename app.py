import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import uuid
from datetime import datetime
from supabase import create_client

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ARIA", page_icon="⚡", layout="wide")

# ── SETUP ─────────────────────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

SYSTEM_PROMPT_BASE = """You are ARIA, Sri's personal AI assistant.
Sri is an AI Engineer at Standard Roofs, Erode, Tamil Nadu, working on a Roofing ERP SaaS built on Zoho One.
Be direct, clear, and helpful. Give complete answers and working code when asked."""

@st.cache_resource
def get_model(system_prompt: str):
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_prompt
    )

@st.cache_resource
def get_sb():
    url = st.secrets.get("SUPABASE_URL", "").strip()
    key = st.secrets.get("SUPABASE_KEY", "").strip()
    if not url or not key or not url.startswith("http"):
        st.session_state["_sb_error"] = f"Missing/invalid config. URL set: {bool(url)}, Key set: {bool(key)}, URL starts with http: {url.startswith('http') if url else False}"
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        st.session_state["_sb_error"] = f"create_client failed: {e}"
        return None

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif !important; }

[data-testid="stAppViewContainer"], .stApp { background:#0a0a10 !important; }
.block-container { max-width: 820px; padding-top: 1.5rem; padding-bottom: 7rem; }
#MainMenu, footer, header { visibility: hidden; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 8px 0 !important;
}
.stChatMessage p, .stChatMessage li, .stChatMessage span { color: #e2e2f0 !important; font-size: 14.5px !important; line-height: 1.7 !important; }

/* User message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg,#1e1b4b,#1a1535);
    border: 1px solid #2d2766;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 16px;
    max-width: 80%;
    margin-left: auto;
}

/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 4px 16px 16px 16px;
    padding: 12px 18px;
}

/* Avatars */
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg,#6c5ce7,#ec4899) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 9px !important;
}
[data-testid="chatAvatarIcon-user"] {
    background: #1e1a3e !important;
    border: 1px solid #2d2766 !important;
    border-radius: 9px !important;
    color: #a29bfe !important;
}

/* Code blocks */
.stChatMessage code {
    background:#1a1a2e !important; border:1px solid #2a2a44 !important;
    border-radius:5px !important; font-size:13px !important; color:#cdd6f4 !important;
    padding:2px 6px !important;
}
.stChatMessage pre {
    background:#11111e !important; border:1px solid #2a2a44 !important;
    border-radius:10px !important; padding:14px !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    background:#16162a !important;
    border:1.5px solid #2a2a44 !important;
    border-radius:14px !important;
}
[data-testid="stChatInput"] textarea {
    background:#16162a !important;
    color:#e0e0f0 !important;
    border:none !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color:#6c5ce7 !important;
    box-shadow: 0 0 0 3px rgba(108,92,231,0.15) !important;
}

/* Sidebar */
[data-testid="stSidebar"] > div:first-child { background:#0d0d18 !important; border-right:1px solid #1a1a2e !important; }
[data-testid="stSidebar"] { background:#0d0d18 !important; }
[data-testid="stSidebar"] button {
    text-align:left !important;
    background:#16162a !important;
    border:1px solid #2a2a44 !important;
    border-radius:8px !important;
    color:#9090b0 !important;
    font-size:12.5px !important;
}
[data-testid="stSidebar"] button:hover {
    border-color:#6c5ce7 !important;
    color:#a29bfe !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
    background:#16162a !important;
    border:1px dashed #2a2a44 !important;
    border-radius:10px !important;
}
[data-testid="stSidebar"] hr { border-color:#1e1e30 !important; }

/* Status pill */
.aria-status {
    display:inline-flex; align-items:center; gap:6px;
    background:#0d2818; border:1px solid #065f46; color:#34d399;
    padding:4px 12px; border-radius:20px; font-size:11px; font-weight:500;
}
.aria-status.off { background:#2a1414; border-color:#7f1d1d; color:#f87171; }
.aria-dot { width:6px; height:6px; border-radius:50%; background:currentColor; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
</style>
""", unsafe_allow_html=True)

# ── DB HELPERS ────────────────────────────────────────────────────────────────
def save_message(session_id: str, role: str, content: str):
    sb = get_sb()
    if sb is None:
        return
    try:
        sb.table("conversations").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception:
        pass

def load_sessions():
    sb = get_sb()
    if sb is None:
        return []
    try:
        r = sb.table("conversations") \
            .select("session_id, content, created_at") \
            .eq("role", "user") \
            .order("created_at", desc=True) \
            .limit(100).execute()
        seen = {}
        for row in r.data:
            sid = row["session_id"]
            if sid not in seen:
                preview = row["content"][:40] + "…" if len(row["content"]) > 40 else row["content"]
                seen[sid] = {"id": sid, "preview": preview}
        return list(seen.values())[:10]
    except Exception:
        return []

def load_messages(session_id: str):
    sb = get_sb()
    if sb is None:
        return []
    try:
        r = sb.table("conversations") \
            .select("role, content") \
            .eq("session_id", session_id) \
            .order("created_at").execute()
        return [{"role": m["role"], "content": m["content"]} for m in r.data]
    except Exception:
        return []

# ── MEMORY HELPERS (long-term facts about Sri) ───────────────────────────────
def save_memory(key: str, value: str):
    sb = get_sb()
    if sb is None:
        return
    try:
        sb.table("memories").upsert({
            "key": key,
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }, on_conflict="key").execute()
    except Exception:
        pass

def load_memories():
    sb = get_sb()
    if sb is None:
        return {}
    try:
        r = sb.table("memories").select("key, value").execute()
        return {row["key"]: row["value"] for row in r.data}
    except Exception:
        return {}

def build_system_prompt():
    memories = load_memories()
    if not memories:
        return SYSTEM_PROMPT_BASE
    mem_text = "\n".join(f"- {k}: {v}" for k, v in memories.items())
    return SYSTEM_PROMPT_BASE + f"\n\n## Things you remember about Sri\n{mem_text}\n\nUse this naturally in conversation when relevant."

# ── PDF HELPER ────────────────────────────────────────────────────────────────
def extract_pdf_text(pdf_file) -> str:
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
sb_connected = get_sb() is not None

with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 14px">
      <div style="width:34px;height:34px;border-radius:9px;flex-shrink:0;
           background:linear-gradient(135deg,#6c5ce7,#ec4899);
           display:flex;align-items:center;justify-content:center;
           font-size:15px;font-weight:800;color:#fff">A</div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#e0e0f0;line-height:1.2">ARIA</div>
        <div style="font-size:10.5px;color:#55556a">Sri's Personal AI</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if sb_connected:
        st.markdown('<span class="aria-status"><span class="aria-dot"></span>Memory Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="aria-status off"><span class="aria-dot"></span>Memory Offline</span>', unsafe_allow_html=True)

    st.write("")
    if st.button("✦  New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    if sb_connected:
        sessions = load_sessions()
        if sessions:
            st.markdown("---")
            st.caption("RECENT CHATS")
            for s in sessions:
                if s["id"] != st.session_state.session_id:
                    if st.button(f"💬 {s['preview']}", key=s["id"], use_container_width=True):
                        st.session_state.session_id = s["id"]
                        st.session_state.messages = load_messages(s["id"])
                        st.rerun()

    st.markdown("---")
    st.caption("UPLOAD FILES")
    uploaded_image = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="img", label_visibility="collapsed")
    uploaded_pdf = st.file_uploader("PDF", type=["pdf"], key="pdf", label_visibility="collapsed")

    if sb_connected:
        st.markdown("---")
        st.caption("🧠 MEMORY")
        memories = load_memories()
        if memories:
            for k, v in memories.items():
                st.markdown(f"<div style='font-size:12px;color:#9090b0;padding:4px 0'><b style=\"color:#a29bfe\">{k}:</b> {v}</div>", unsafe_allow_html=True)
        else:
            st.caption("No memories yet — tell ARIA something to remember!")

        with st.expander("➕ Add manually"):
            mk = st.text_input("Key", key="mem_key", label_visibility="collapsed", placeholder="Key (e.g. company)")
            mv = st.text_input("Value", key="mem_val", label_visibility="collapsed", placeholder="Value (e.g. Standard Roofs)")
            if st.button("Save", use_container_width=True):
                if mk and mv:
                    save_memory(mk, mv)
                    st.rerun()
    else:
        st.markdown("---")
        st.caption("🧠 Memory needs Supabase keys in Secrets to work. Chat still works fine without it.")
        if "_sb_error" in st.session_state:
            st.code(st.session_state["_sb_error"], language=None)

# ── MAIN ──────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
         min-height:55vh;text-align:center;padding:40px 20px">
      <div style="width:64px;height:64px;border-radius:18px;margin:0 auto 20px;
           background:linear-gradient(135deg,#6c5ce7,#ec4899);
           display:flex;align-items:center;justify-content:center;
           font-size:28px;font-weight:800;color:#fff;
           box-shadow:0 0 50px rgba(108,92,231,.35)">A</div>
      <h2 style="font-size:24px;font-weight:700;margin:0 0 8px;
           background:linear-gradient(135deg,#a29bfe,#f472b6);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        Hey Sri, ARIA here.
      </h2>
      <p style="color:#55556a;font-size:13.5px;max-width:380px;line-height:1.7">
        Ask me anything, upload an image or PDF, or just say hi.
      </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

prompt = st.chat_input("Ask ARIA anything...")

if prompt:
    gemini_parts = [prompt]
    display_prompt = prompt

    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        gemini_parts.append(img)
        display_prompt += "\n\n📎 *[Image attached]*"

    if uploaded_pdf is not None:
        pdf_text = extract_pdf_text(uploaded_pdf)
        gemini_parts.append(f"\n\n--- PDF Content ---\n{pdf_text[:15000]}")
        display_prompt += f"\n\n📎 *[PDF attached: {uploaded_pdf.name}]*"

    with st.chat_message("user"):
        st.markdown(display_prompt)
    st.session_state.messages.append({"role": "user", "content": display_prompt})
    save_message(st.session_state.session_id, "user", display_prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            system_prompt = build_system_prompt()
            model = get_model(system_prompt)

            history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=history)
            response = chat.send_message(gemini_parts, stream=True)

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ Error: {str(e)}"
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_message(st.session_state.session_id, "assistant", full_response)

    # ── Simple auto-memory: detect "remember" statements ──
    lower_prompt = prompt.lower()
    if "remember" in lower_prompt or "my name is" in lower_prompt or "i am" in lower_prompt:
        try:
            mem_model = genai.GenerativeModel("gemini-2.5-flash")
            extraction = mem_model.generate_content(
                f"""Extract a short fact worth remembering long-term from this message, if any.
Reply ONLY in format: key: value
If nothing worth remembering, reply: NONE

Message: "{prompt}\""""
            )
            text = extraction.text.strip()
            if text and text != "NONE" and ":" in text:
                k, v = text.split(":", 1)
                save_memory(k.strip(), v.strip())
        except Exception:
            pass

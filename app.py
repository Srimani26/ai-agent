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
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"], .stApp { background:#0a0a10; }
.block-container { max-width: 800px; padding-top: 2rem; padding-bottom: 6rem; }
#MainMenu, footer, header { visibility: hidden; }
.stChatMessage p, .stChatMessage li { color: #e0e0f0 !important; }
[data-testid="stChatInput"] textarea {
    background:#16162a !important;
    color:#e0e0f0 !important;
    border:1px solid #2a2a44 !important;
    border-radius:14px !important;
}
[data-testid="stSidebar"] button {
    text-align:left !important;
}
</style>
""", unsafe_allow_html=True)

# ── DB HELPERS ────────────────────────────────────────────────────────────────
def save_message(session_id: str, role: str, content: str):
    try:
        get_sb().table("conversations").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        st.toast(f"Save failed: {e}")

def load_sessions():
    try:
        r = get_sb().table("conversations") \
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
    try:
        r = get_sb().table("conversations") \
            .select("role, content") \
            .eq("session_id", session_id) \
            .order("created_at").execute()
        return [{"role": m["role"], "content": m["content"]} for m in r.data]
    except Exception:
        return []

# ── MEMORY HELPERS (long-term facts about Sri) ───────────────────────────────
def save_memory(key: str, value: str):
    try:
        get_sb().table("memories").upsert({
            "key": key,
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }, on_conflict="key").execute()
    except Exception as e:
        st.toast(f"Memory save failed: {e}")

def load_memories():
    try:
        r = get_sb().table("memories").select("key, value").execute()
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
with st.sidebar:
    st.markdown("### ⚡ ARIA")
    st.caption("Sri's Personal AI — Phase 3 (Memory)")

    if st.button("✦ New Chat", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Recent Chats**")
    for s in load_sessions():
        if s["id"] != st.session_state.session_id:
            if st.button(f"💬 {s['preview']}", key=s["id"], use_container_width=True):
                st.session_state.session_id = s["id"]
                st.session_state.messages = load_messages(s["id"])
                st.rerun()

    st.markdown("---")
    st.markdown("**Upload Files**")
    uploaded_image = st.file_uploader("Image", type=["png", "jpg", "jpeg"], key="img")
    uploaded_pdf = st.file_uploader("PDF", type=["pdf"], key="pdf")

    st.markdown("---")
    st.markdown("**🧠 Memory**")
    memories = load_memories()
    if memories:
        for k, v in memories.items():
            st.caption(f"**{k}:** {v}")
    else:
        st.caption("No memories yet. Tell ARIA something to remember!")

    with st.expander("➕ Add memory manually"):
        mk = st.text_input("Key", key="mem_key")
        mv = st.text_input("Value", key="mem_val")
        if st.button("Save memory", use_container_width=True):
            if mk and mv:
                save_memory(mk, mv)
                st.rerun()

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.title("⚡ ARIA")
st.caption("I remember you, Sri.")

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

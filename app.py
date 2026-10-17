import streamlit as st
from groq import Groq
from supabase import create_client, Client
import time

# Page configuration
st.set_page_config(page_title="Orvylith AI", page_icon="🤖", layout="wide")

# API Clients initialization
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Orvylith AI, created by Rudra. "
        "CRITICAL RULES: "
        "1. You are strictly a text-only assistant (V1.0). "
        "2. You CANNOT view, process, or accept images. "
        "3. If asked about image upload or image processing, clearly say: "
        "'Main abhi images process nahi kar sakta, yeh feature agle update (V2.0) me aayega.' "
        "4. Do NOT hallucinate, lie, or invent buttons/menus that do not exist."
    )
}

# Supabase Helper Functions
def get_all_chats():
    try:
        res = supabase.table("chats").select("id, title").order("id", desc=True).execute()
        return res.data or []
    except Exception:
        return []

def get_chat_messages(chat_id):
    try:
        res = supabase.table("chats").select("messages").eq("id", chat_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["messages"]
    except Exception:
        pass
    return [SYSTEM_PROMPT]

def save_chat_to_db(chat_id, title, messages):
    try:
        supabase.table("chats").upsert({
            "id": chat_id,
            "title": title,
            "messages": messages
        }).execute()
    except Exception as e:
        st.error(f"Save failed: {e}")

# Session State Initialization
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_PROMPT]

# --- SIDEBAR: Multi-Chat History ---
with st.sidebar:
    st.title("Orvylith AI")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = None
        st.session_state.messages = [SYSTEM_PROMPT]
        st.rerun()

    st.markdown("---")
    st.subheader("Previous Chats")
    chats = get_all_chats()
    for c in chats:
        btn_label = c.get("title") or f"Chat {c['id']}"
        if st.button(btn_label, key=f"chat_{c['id']}", use_container_width=True):
            st.session_state.current_chat_id = c["id"]
            st.session_state.messages = get_chat_messages(c["id"])
            st.rerun()

# --- MAIN SCREEN: Render Existing Chat ---
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# --- USER INPUT & AI GENERATION ---
if prompt := st.chat_input("Message Orvylith..."):
    # 1. User message show karo aur state me jodo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 2. AI response generate karo
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=st.session_state.messages,
            temperature=0.2,
        )
        reply = response.choices[0].message.content

        # 3. Assistant reply list me daalo
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 4. Supabase cloud database me save karo
        if st.session_state.current_chat_id is None:
            new_id = int(time.time())
            chat_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
            st.session_state.current_chat_id = new_id
            save_chat_to_db(new_id, chat_title, st.session_state.messages)
        else:
            save_chat_to_db(st.session_state.current_chat_id, prompt[:20], st.session_state.messages)

        # 5. Page ko fresh state ke sath reload karo taaki duplicate print na ho
        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

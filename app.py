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

def delete_chat_from_db(chat_id):
    try:
        supabase.table("chats").delete().eq("id", chat_id).execute()
    except Exception as e:
        st.error(f"Delete failed: {e}")

def generate_smart_title(first_message):
    try:
        res = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "Generate a concise 2-4 word title for this chat topic. Return ONLY the title, no quotes or punctation."},
                {"role": "user", "content": first_message}
            ],
            temperature=0.3,
        )
        return res.choices[0].message.content.strip()
    except Exception:
        return first_message[:20] + "..." if len(first_message) > 20 else first_message

# Session State Initialization
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_PROMPT]

# --- SIDEBAR: Multi-Chat & Delete Management ---
with st.sidebar:
    st.title("Orvylith AI")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_chat_id = None
        st.session_state.messages = [SYSTEM_PROMPT]
        st.rerun()

    st.markdown("---")
    st.subheader("Chat History")
    chats = get_all_chats()
    for c in chats:
        col1, col2 = st.columns([0.8, 0.2])
        btn_label = c.get("title") or f"Chat {c['id']}"
        with col1:
            if st.button(btn_label, key=f"chat_{c['id']}", use_container_width=True):
                st.session_state.current_chat_id = c["id"]
                st.session_state.messages = get_chat_messages(c["id"])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{c['id']}"):
                delete_chat_from_db(c["id"])
                if st.session_state.current_chat_id == c["id"]:
                    st.session_state.current_chat_id = None
                    st.session_state.messages = [SYSTEM_PROMPT]
                st.rerun()

# --- MAIN SCREEN ---
is_new_chat = len([m for m in st.session_state.messages if m["role"] != "system"]) == 0

if is_new_chat:
    st.markdown("### 👋 Welcome to Orvylith AI")
    st.caption("Main aapka personal AI assistant hoon. Kuch bhi puch sakte hain!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 Koi naya topic explain karo", use_container_width=True):
            st.session_state.temp_prompt = "Mujhe Artificial Intelligence ke baare me simple shabdon me batao."
            st.rerun()
    with col2:
        if st.button("💻 Python code likhne me madad", use_container_width=True):
            st.session_state.temp_prompt = "Python me ek basic calculator ka code likho."
            st.rerun()

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Quick prompt handle karna
prompt = st.chat_input("Message Orvylith...")
if "temp_prompt" in st.session_state and st.session_state.temp_prompt:
    prompt = st.session_state.temp_prompt
    st.session_state.temp_prompt = None

# --- USER INPUT & STREAMING GENERATION ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Live Typewriter Streaming Effect
        with st.chat_message("assistant"):
            def get_stream():
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=st.session_state.messages,
                    stream=True,
                    temperature=0.2,
                )
                for chunk in completion:
                    content = chunk.choices[0].delta.content or ""
                    yield content

            reply = st.write_stream(get_stream())

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Save to Database with Smart Title
        if st.session_state.current_chat_id is None:
            new_id = int(time.time())
            smart_title = generate_smart_title(prompt)
            st.session_state.current_chat_id = new_id
            save_chat_to_db(new_id, smart_title, st.session_state.messages)
        else:
            save_chat_to_db(st.session_state.current_chat_id, prompt[:20], st.session_state.messages)

        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

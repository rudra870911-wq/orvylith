import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(page_title="Orvylith AI", page_icon="⚡", layout="centered")

# Custom Styling (Dark & Sleek look)
st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# Sidebar - Developer Profile
with st.sidebar:
    st.title("⚡ Orvylith")
    st.caption("Next-Gen Personal AI Assistant")
    st.write("---")
    st.subheader("👨‍💻 About Developer")
    st.write("**Name:** Rudra")
    st.write("**Role:** Founder & AI Developer")
    st.write("**About:** Built by Rudra as a dedicated conversational intelligence project.")
    st.write("---")
    st.caption("System Status: 🟢 Fully Operational")

# Header
st.title("⚡ Orvylith AI")
st.write("Welcome! I am Orvylith, an AI assistant developed by **Rudra**.")
st.caption("Ask me anything — general queries, ideas, or questions about my creation.")

# Groq API Client Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# System prompt giving identity to Orvylith
system_prompt = (
    "Your name is Orvylith. You are an intelligent, polite, and articulate personal AI assistant. "
    "You were designed and developed solely by Rudra. "
    "Whenever a user asks 'Who made you?', 'Tumhe kisne banaya?', 'Who is your creator/developer?', "
    "or asks about your origin, always answer with pride and respect that you were created by Rudra. "
    "Respond naturally in English or Hinglish/Hindi based on how the user talks to you. "
    "Keep answers helpful, engaging, and accurate."
)

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input from user
if prompt := st.chat_input("Message Orvylith..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages_payload,
    )
    reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

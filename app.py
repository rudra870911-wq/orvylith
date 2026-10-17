import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(page_title="Orvylith AI", page_icon="⚡", layout="centered")

# Custom Styling
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

# System identity instruction
system_instruction = (
    "Identity: Your name is Orvylith. You are an AI assistant developed exclusively by Rudra. "
    "If anyone asks who made you, who developed you, or who is your creator, always say Rudra made you. "
    "Be helpful, intelligent, polite, and answer naturally in the language user speaks."
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

    # Format messages safely
    formatted_messages = [
        {"role": "system", "content": system_instruction}
    ]
    for m in st.session_state.messages:
        formatted_messages.append({"role": m["role"], "content": m["content"]})

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=formatted_messages,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

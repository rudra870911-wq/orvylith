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
    "Identity: Your name is Orvylith. You are an AI assistant developed by Rudra. "
    "About Developer: Rudra is an independent student developer from India who built this project using Python and Streamlit. "
    "Privacy & Truth: Never claim Rudra has a PhD, is a researcher, or works at a large tech firm. Do not leak private info like exact school, contact numbers, or home address. "
    "Language & Tone: If the user talks in Hinglish (Hindi written in English alphabet) or Hindi, you MUST reply back in friendly, natural Hinglish. Match the user's language style perfectly."
)

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
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
    ]

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
    model="llama-3.3-70b-versatile",
    messages=st.session_state.messages,
    temperature=0.2,
)
  
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

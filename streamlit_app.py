# streamlit_app.py

# --------------------------- STAGE 1: IMPORTS ---------------------------

import os                          # Handles operating system interactions (e.g., env variables)
import re                          # For cleaning responses using regex
import streamlit as st             # Streamlit framework for web interface
from dotenv import load_dotenv     # Loads environment variables from a .env file
from llm import CustomerSupportAssistant  # Custom class to interact with LLM backend


# --------------------------- STAGE 2: ENVIRONMENT SETUP ---------------------------

load_dotenv()                                 # Load variables from .env file
api_key = os.getenv("GROQ_API_KEY")           # Securely fetch API key from environment


# --------------------------- STAGE 3: ASSISTANT INITIALIZATION ---------------------------

assistant = CustomerSupportAssistant(api_key)  # Instantiate the LLM assistant


# --------------------------- STAGE 4: STREAMLIT PAGE CONFIG ---------------------------

st.set_page_config(
    page_title="Banking Support Chat",  # Browser tab title
    page_icon="💬"                      # Browser tab icon
)

st.title("💬 FinBank Customer Support Assistant")  # App header
st.markdown("Ask me anything related to your bank account, transactions, security, or mobile banking.")  # Subtext


# --------------------------- STAGE 5: SESSION STATE ---------------------------

# Create a persistent chat history
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []


# --------------------------- STAGE 6: USER INPUT ---------------------------

user_input = st.chat_input("Type your question here...")  # Input bar at the bottom

if user_input:
    # Store user input in session
    st.session_state.chat_log.append({
        "role": "user",
        "content": user_input
    })


    # --------------------------- STAGE 7: LLM RESPONSE ---------------------------

    raw_response = assistant.get_response(user_input)  # Get raw output from assistant

    # Clean LLM output: remove <think>...</think> tags if present
    clean_response = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip()

    # Save clean response to chat history
    st.session_state.chat_log.append({
        "role": "assistant",
        "content": clean_response
    })


# --------------------------- STAGE 8: CHAT DISPLAY ---------------------------

# Display each message in chat format
for message in st.session_state.chat_log:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(message["content"])

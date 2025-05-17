import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any, Optional

# App title and configuration
st.set_page_config(
    page_title="Ollama GUI",
    page_icon="💀",
    layout="wide",
)

# Constants
OLLAMA_API_BASE = "http://localhost:11434/api"
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."

# Custom CSS to improve the UI

st.markdown("""
<style>
    .user-message {
        background-color: #e6f7ff;
        color: #000000;  /* black text */
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .assistant-message {
        background-color: #f0f0f0;
        color: #000000;  /* black text */
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .stTextInput {
        padding-bottom: 10px;
    }
    .main-header {
        text-align: center;
    }
    /* Fix for input text area */
    textarea, input[type="text"] {
        color: #262730 !important;  /* dark text */
        background-color: #ffffff !important;  /* white background */
    }
    .stTextArea textarea {
        color: #262730 !important;  /* dark text */
        background-color: #ffffff !important;  /* white background */
    }
    /* Make sure sidebar text is visible too */
    .stSlider label, .stNumberInput label, .stSelectbox label, .stTextarea label {
        color: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar for model selection and settings
st.sidebar.title("Model Settings")

# Function to get available models from Ollama
@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_available_models() -> List[str]:
    try:
        response = requests.get(f"{OLLAMA_API_BASE}/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        else:
            st.error(f"Failed to get models: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to Ollama: {str(e)}")
        return []

# Get available models
available_models = get_available_models()

if not available_models:
    st.warning("⚠️ No models found or Ollama service not running. Make sure Ollama is installed and running.")
    st.stop()

# Model selection dropdown
selected_model = st.sidebar.selectbox(
    "Select Model",
    available_models,
    index=0 if available_models else None,
)

# Advanced settings with expander
with st.sidebar.expander("Advanced Settings"):
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1,
                           help="Higher values make output more random, lower values make it more deterministic")
    
    max_tokens = st.number_input("Max Tokens", min_value=10, max_value=4096, value=2000, step=10,
                                help="Maximum length of response")
    
    system_prompt = st.text_area("System Prompt", value=DEFAULT_SYSTEM_PROMPT, height=100,
                                help="Instructions that guide the model's behavior")

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

# Initialize session state for chat messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main app header
st.markdown("<h1 class='main-header'>Ollama Gui</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 class='main-header'>Currently using: {selected_model}</h3>", unsafe_allow_html=True)

# Function to call Ollama API
def chat_with_ollama(messages: List[Dict[str, str]], model: str, temp: float, max_len: int) -> Optional[str]:
    try:
        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temp,
                "max_tokens": max_len,
            },
            "stream": False
        }
        
        response = requests.post(f"{OLLAMA_API_BASE}/chat", json=payload)
        
        if response.status_code == 200:
            return response.json().get("message", {}).get("content", "No response")
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Display chat messages
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        st.markdown(f"<div class='user-message'><strong>You:</strong> {content}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-message'><strong>AI:</strong> {content}</div>", unsafe_allow_html=True)

# User input area
user_input = st.text_area("Type your message:", key="user_input", height=100)

# Format messages for API call
def format_messages_for_api():
    # First add the system prompt if there are no messages yet
    if not st.session_state.messages:
        return [{"role": "system", "content": system_prompt}]
    
    # Otherwise, make sure the first one is the system message
    messages_for_api = []
    
    # Check if first message is system, if not add it
    if st.session_state.messages and st.session_state.messages[0]["role"] != "system":
        messages_for_api.append({"role": "system", "content": system_prompt})
    
    # Add all conversation messages
    messages_for_api.extend(st.session_state.messages)
    return messages_for_api

# Send button
if st.button("Send") and user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get messages formatted for API
    api_messages = format_messages_for_api()
    
    # Show "AI is thinking..." message
    with st.spinner("AI is thinking..."):
        # Call API
        response = chat_with_ollama(
            messages=api_messages,
            model=selected_model,
            temp=temperature,
            max_len=max_tokens
        )
    
    # Add response to chat if successful
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    # Force a rerun to update the UI
    st.rerun()

# Footer
st.markdown("---")

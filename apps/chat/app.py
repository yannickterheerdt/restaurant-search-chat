import os
import sys
import streamlit as st
from typing import Dict, List
from llama_index.core.base.llms.types import MessageRole, ChatMessage

# Ensure the correct module path is added to sys.path for imports
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from rag import RAG

def map_message(message_dict: Dict[str, str]) -> ChatMessage:
    """
    Maps a message dictionary to a ChatMessage object, converting the role
    to the appropriate MessageRole enum.

    Args:
        message_dict (Dict[str, str]): Dictionary containing message 'role' and 'content'.

    Returns:
        ChatMessage: A ChatMessage object with the role and content mapped.
    """
    role_mapping = {
        'assistant': MessageRole.ASSISTANT,
        'user': MessageRole.USER,
        'system': MessageRole.SYSTEM
    }
    return ChatMessage(content=message_dict['content'], role=role_mapping[message_dict['role']])

def display_chat_history() -> None:
    """
    Displays the chat history from Streamlit's session state.
    Each message is rendered in a separate chat box based on its role.
    """
    for message in st.session_state['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

def handle_user_input() -> None:
    """
    Handles user input by appending it to the session state,
    displaying it in the chat, and generating the assistant's response.
    """
    if prompt := st.chat_input("Stel een vraag"):
        st.session_state['messages'].append({'role': 'user', 'content': prompt})
        
        # Display the user message
        with st.chat_message('user'):
            st.markdown(prompt)

        response_text = ""
        chat_history = [map_message(message) for message in st.session_state['messages']]
        
        # Display assistant response progressively in a single chat box
        with st.chat_message('assistant'):
            assistant_placeholder = st.empty()
            for chunk in rag.generate_response(prompt, chat_history):
                response_text += chunk
                assistant_placeholder.markdown(response_text)

        st.session_state['messages'].append({'role': 'assistant', 'content': response_text})

# Initialize RAG agent
rag = RAG()
rag.load_agent()

# Main execution
st.title("Restaurant Chat")
st.session_state.setdefault('messages', [])
display_chat_history()
handle_user_input()

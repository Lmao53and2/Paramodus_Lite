import streamlit as st
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.groq import Groq
from agno.models.perplexity import Perplexity
from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Paramodus AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Paramodus AI Assistant")
st.markdown("---")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Provider Selection
    provider_options = []
    if os.getenv("OPENAI_API_KEY"):
        provider_options.append("OpenAI")
    if os.getenv("GROQ_API_KEY"):
        provider_options.append("Groq") 
    if os.getenv("PERPLEXITY_API_KEY"):
        provider_options.append("Perplexity")
    
    if not provider_options:
        st.warning("No API keys found in .env file")
        st.info("Please add API keys to your .env file")
        st.stop()
    
    selected_provider = st.selectbox("Choose AI Provider", provider_options)
    
    # Model selection based on provider
    if selected_provider == "OpenAI":
        model_name = st.selectbox("Select Model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
        api_key = os.getenv("OPENAI_API_KEY")
        model = OpenAIChat(id=model_name, api_key=api_key)
    elif selected_provider == "Groq":
        model_name = st.selectbox("Select Model", ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"])
        api_key = os.getenv("GROQ_API_KEY")
        model = Groq(id=model_name, api_key=api_key)
    elif selected_provider == "Perplexity":
        model_name = st.selectbox("Select Model", ["sonar", "sonar-pro"])
        api_key = os.getenv("PERPLEXITY_API_KEY")
        model = Perplexity(id=model_name, api_key=api_key)
    
    st.markdown("---")
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = None
        st.rerun()

# Create agent if not exists
if st.session_state.agent is None:
    try:
        # Create database
        db = SqliteDb(db_file="paramodus_agent.db")
        
        # Create agent
        st.session_state.agent = Agent(
            model=model,
            db=db,
            instructions="""
                You are a helpful AI assistant called Paramodus.
                You provide clear, accurate, and helpful responses.
                Be conversational and friendly while maintaining professionalism.
                If you don't know something, say so honestly.
            """,
            markdown=True,
        )
        
    except Exception as e:
        st.error(f"Error creating agent: {str(e)}")
        st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = st.session_state.agent.run(prompt)
                content = response.content if hasattr(response, 'content') else str(response)
            
            st.markdown(content)
            st.session_state.messages.append({"role": "assistant", "content": content})
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
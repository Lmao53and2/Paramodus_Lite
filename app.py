import streamlit as st
import os
import tempfile
from agno.agent import Agent
from agno.models.perplexity import Perplexity
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.knowledge.reader.pdf_reader import PDFReader
from load_storage import load_session_storage, load_personality_storage, load_task_storage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Paramodus Lite",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("🔑 API Configuration")
    
    pplx_key = os.getenv("PERPLEXITY_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    oai_key = os.getenv("OPENAI_API_KEY")

    available_providers = []
    if pplx_key: available_providers.append("Perplexity")
    if groq_key: available_providers.append("Groq")
    if oai_key: available_providers.append("OpenAI")

    if not available_providers:
        st.warning("No API keys found in .env. Please configure them.")
        selected_provider = st.selectbox("Select Provider", ["OpenAI", "Groq", "Perplexity"])
        user_key = st.text_input(f"Enter {selected_provider} API Key", type="password")
        if user_key:
            current_api_key = user_key
        else:
            st.stop()
    else:
        selected_provider = st.selectbox("Select Provider", available_providers)
        if selected_provider == "Perplexity":
            current_api_key = pplx_key
        elif selected_provider == "Groq":
            current_api_key = groq_key
        else:
            current_api_key = oai_key

    # Model Selection
    if selected_provider == "Perplexity":
        model_id = st.selectbox("Model", ["sonar", "sonar-pro"])
    elif selected_provider == "Groq":
        model_id = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"])
    else:
        model_id = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])

    st.divider()
    
    # Task Manager UI
    st.header("📋 Task Manager")
    if st.session_state.tasks:
        for i, task in enumerate(st.session_state.tasks):
            t_col1, t_col2 = st.columns([0.8, 0.2])
            with t_col1:
                is_done = st.checkbox(task["text"], key=f"task_check_{i}", value=task.get("completed", False))
                st.session_state.tasks[i]["completed"] = is_done
            with t_col2:
                if st.button("🗑️", key=f"task_del_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()
    
    new_manual_task = st.text_input("Add task manually...", key="manual_input")
    if st.button("Add Task") and new_manual_task:
        st.session_state.tasks.append({"text": new_manual_task, "completed": False, "source": "manual"})
        st.rerun()

    if st.button("🗑️ Clear All Tasks", use_container_width=True):
        st.session_state.tasks = []
        st.rerun()

    st.divider()
    if st.button("💬 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Agent Factory ---
@st.cache_resource
def create_model_instance(provider_name, model_name, api_key):
    if provider_name == "Perplexity":
        return Perplexity(id=model_name, api_key=api_key)
    elif provider_name == "Groq":
        return Groq(id=model_name, api_key=api_key)
    return OpenAIChat(id=model_name, api_key=api_key)

@st.cache_resource
def get_cached_agent(provider_name, model_name, api_key, agent_role):
    model = create_model_instance(provider_name, model_name, api_key)
    
    if agent_role == "personality":
        return Agent(
            model=model,
            db=load_personality_storage(),
            instructions="Analyze the user's personality based on the chat. Be concise. Use Markdown.",
            markdown=True
        )
    elif agent_role == "task":
        return Agent(
            model=model,
            db=load_task_storage(),
            instructions="Extract actionable tasks from the conversation. Return only a markdown list starting with '- '.",
            markdown=True
        )
    else:
        return Agent(
            model=model,
            db=load_session_storage(),
            instructions="You are Paramodus, a helpful AI assistant. Answer accurately. Use LaTeX for math: $inline$ and $$block$$.",
            markdown=True
        )

# Initialize Agents
main_agent = get_cached_agent(selected_provider, model_id, current_api_key, "main")
task_agent = get_cached_agent(selected_provider, model_id, current_api_key, "task")
personality_agent = get_cached_agent(selected_provider, model_id, current_api_key, "personality")

# --- Main UI ---
st.title("🤖 Paramodus Lite")

# PDF Upload
uploaded_pdf = st.file_uploader("Upload PDF context", type="pdf")
if uploaded_pdf and not st.session_state.pdf_text:
    with st.spinner("Processing PDF..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(uploaded_pdf.getvalue())
                tmp_path = tmp_pdf.name
            
            pdf_reader = PDFReader()
            pdf_docs = pdf_reader.read(tmp_path)
            st.session_state.pdf_text = "\n".join([d.content for d in pdf_docs if d.content])
            
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            st.success("PDF Context Loaded!")
        except Exception as e:
            st.error(f"Failed to process PDF: {e}")

# Chat History
for chat_msg in st.session_state.messages:
    with st.chat_message(chat_msg["role"]):
        st.markdown(chat_msg["content"])

# Chat Input
if user_prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        agent_prompt = f"PDF Context:\n{st.session_state.pdf_text}\n\nUser: {user_prompt}" if st.session_state.pdf_text else user_prompt
        
        with st.spinner("Thinking..."):
            try:
                agent_response = main_agent.run(agent_prompt)
                resp_content = agent_response.content if hasattr(agent_response, 'content') else str(agent_response)
                st.markdown(resp_content)
                st.session_state.messages.append({"role": "assistant", "content": resp_content})
            except Exception as e:
                st.error(f"Error: {e}")

        # Background Task Extraction
        try:
            extraction_res = task_agent.run(f"Extract tasks from: {user_prompt}")
            extraction_content = extraction_res.content if hasattr(extraction_res, 'content') else str(extraction_res)
            for line in extraction_content.split('\n'):
                if line.strip().startswith('- '):
                    task_text = line.strip()[2:]
                    if task_text.lower() not in [t["text"].lower() for t in st.session_state.tasks]:
                        st.session_state.tasks.append({"text": task_text, "completed": False, "source": "auto"})
        except Exception:
            pass

# Analysis Expanders
if st.session_state.messages:
    analysis_col1, analysis_col2 = st.columns(2)
    with analysis_col1:
        with st.expander("🧠 Personality Analysis"):
            if st.button("Update Analysis"):
                try:
                    p_analysis = personality_agent.run(f"Analyze: {st.session_state.messages[-2:]}")
                    st.markdown(p_analysis.content if hasattr(p_analysis, 'content') else str(p_analysis))
                except Exception as e:
                    st.error(f"Analysis error: {e}")
    with analysis_col2:
        with st.expander("📋 Task Insights"):
            st.write(f"Total Tasks: {len(st.session_state.tasks)}")
            st.write("Check the sidebar for the full task list.")

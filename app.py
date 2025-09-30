import streamlit as st
from agno.agent import Agent
from agno.models.perplexity import Perplexity
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from load_storage import load_session_storage, load_personality_storage, load_task_storage
from agno.knowledge.reader.pdf_reader import PDFReader
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# LaTeX processing functions
def process_latex_content(content):
    """Convert LaTeX expressions to Streamlit-compatible format"""
    if not content:
        return content
    
    # Protect code blocks from LaTeX processing
    code_blocks = []
    def replace_code(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # Protect inline code and code blocks
    content = re.sub(r'``````', replace_code, content)
    content = re.sub(r'`[^`]+`', replace_code, content)
    
    # Convert LaTeX delimiters to Streamlit format
    # Display math: \[ ... \] -> $$ ... $$
    content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', content, flags=re.DOTALL)
    
    # Inline math: \( ... \) -> $ ... $
    content = re.sub(r'\\\((.*?)\\\)', r'$\1$', content, flags=re.DOTALL)
    
    # Restore code blocks
    for i, code_block in enumerate(code_blocks):
        content = content.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return content

def display_content_with_latex(content, font_family="Arial"):
    """Display content with proper LaTeX rendering and font styling"""
    if not content:
        return
    
    # Process LaTeX expressions
    processed_content = process_latex_content(content)
    
    # Check if content contains LaTeX expressions
    has_latex = ('$$' in processed_content or 
                '$' in processed_content and not processed_content.count('$') % 2)
    
    if has_latex:
        # Use regular markdown for LaTeX content (Streamlit handles LaTeX in markdown)
        st.markdown(processed_content)
    else:
        # Use styled HTML for regular text
        st.markdown(
            f"<span style='font-family:{font_family},sans-serif'>{processed_content}</span>", 
            unsafe_allow_html=True
        )

def display_mixed_content(content, font_family="Arial"):
    """Handle mixed content with both LaTeX and regular text"""
    if not content:
        return
    
    processed_content = process_latex_content(content)
    
    # Split content by LaTeX expressions and process each part
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', processed_content, flags=re.DOTALL)
    
    for part in parts:
        if part.strip():
            if (part.startswith('$$') and part.endswith('$$')) or (part.startswith('$') and part.endswith('$') and not part.startswith('$$')):
                # This is a LaTeX expression
                st.markdown(part)
            else:
                # This is regular text
                if part.strip():
                    st.markdown(
                        f"<span style='font-family:{font_family},sans-serif'>{part}</span>", 
                        unsafe_allow_html=True
                    )

# Sidebar API setup
st.sidebar.header("🔑 API Configuration")
pplx_api_key = os.getenv("PERPLEXITY_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

available_providers = []
if pplx_api_key:
    available_providers.append("Perplexity")
if groq_api_key:
    available_providers.append("Groq")
if openai_api_key:
    available_providers.append("OpenAI")

if not available_providers:
    st.sidebar.warning("No API keys found in .env file")
    provider_choice = st.sidebar.selectbox("Choose API Provider:", ["Perplexity", "Groq", "OpenAI"])
    if provider_choice == "Perplexity":
        pplx_api_key = st.sidebar.text_input("Enter Perplexity API Key:", type="password")
        if pplx_api_key:
            os.environ["PERPLEXITY_API_KEY"] = pplx_api_key
    elif provider_choice == "Groq":
        groq_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
        if groq_api_key:
            os.environ["GROQ_API_KEY"] = groq_api_key
    elif provider_choice == "OpenAI":
        openai_api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    st.sidebar.success(f"Available providers: {', '.join(available_providers)}")
    provider_choice = st.sidebar.selectbox("Choose API Provider:", available_providers)

# Model selection
if provider_choice == "Perplexity" and pplx_api_key:
    model_options = ["sonar", "sonar-pro"]
    selected_model = st.sidebar.selectbox("Select Model:", model_options)
    current_api_key = pplx_api_key
elif provider_choice == "Groq" and groq_api_key:
    model_options = ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]
    selected_model = st.sidebar.selectbox("Select Model:", model_options)
    current_api_key = groq_api_key
elif provider_choice == "OpenAI" and openai_api_key:
    model_options = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    selected_model = st.sidebar.selectbox("Select Model:", model_options)
    current_api_key = openai_api_key
else:
    st.sidebar.error("Please provide a valid API key")
    current_api_key = None
    selected_model = None

def create_model_instance(provider, model_name, api_key):
    if provider == "Perplexity":
        return Perplexity(id=model_name, api_key=api_key)
    elif provider == "Groq":
        return Groq(id=model_name, api_key=api_key)
    elif provider == "OpenAI":
        return OpenAIChat(id=model_name, api_key=api_key)

# File upload
pdf_text = ""
uploaded_pdf = st.file_uploader("Upload a PDF for context", type="pdf")
if uploaded_pdf:
    reader = PDFReader()
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_pdf.read())
    documents = reader.read("temp_uploaded.pdf")
    pdf_text = "\n".join([doc.content for doc in documents if doc.content])
    st.success("PDF loaded and text extracted!")

# Sidebar task manager
with st.sidebar:
    st.header("📋 Task Manager")
    if st.session_state.tasks:
        st.subheader("Current Tasks:")
        for i, task in enumerate(st.session_state.tasks):
            col1, col2 = st.columns([4, 1])
            with col1:
                completed = st.checkbox(task["text"], key=f"task_{i}", value=task.get("completed", False))
                if completed != task.get("completed", False):
                    st.session_state.tasks[i]["completed"] = completed
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.tasks.pop(i)
                    st.rerun()
    else:
        st.info("No tasks yet. Start chatting to extract tasks!")

    st.subheader("Add Manual Task:")
    manual_task = st.text_input("Enter a task:", key="manual_task_input")
    if st.button("Add Task") and manual_task:
        st.session_state.tasks.append({
            "text": manual_task,
            "completed": False,
            "source": "manual"
        })
        st.rerun()

    if st.session_state.tasks and st.button("Clear All Tasks"):
        st.session_state.tasks = []
        st.rerun()

    st.markdown("---")
    font_options = ["Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Times New Roman", "Trebuchet MS", "Verdana"]
    selected_font = st.selectbox("Choose chat font", font_options, index=0, key="font_select")
    st.session_state.selected_font = selected_font
    st.markdown(f"""
        <style>
        html, body, [class^='st-'] {{
            font-family: '{selected_font}', sans-serif !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# Agent creation with LaTeX-aware instructions - simplified for Agno v2.0
@st.cache_resource
def create_personality_agent(provider, model_name, api_key):
    return Agent(
        model=create_model_instance(provider, model_name, api_key),
        db=load_personality_storage(),
        instructions="""
            Summarize the conversation and give a brief personality analysis.
            When including mathematical expressions, use proper LaTeX formatting:
            - Use \\( and \\) for inline math
            - Use \\[ and \\] for display math
        """,
        markdown=True,
    )

@st.cache_resource
def create_task_agent(provider, model_name, api_key):
    return Agent(
        model=create_model_instance(provider, model_name, api_key),
        db=load_task_storage(),
        instructions="""
            Extract actionable tasks. Return as list, one per line starting with '- '.
            When including mathematical expressions, use proper LaTeX formatting:
            - Use \\( and \\) for inline math
            - Use \\[ and \\] for display math
        """,
        markdown=True,
    )

@st.cache_resource
def create_main_agent(provider, model_name, api_key, _personality_agent, _task_agent):
    return Agent(
        model=create_model_instance(provider, model_name, api_key),
        db=load_session_storage(),
        team=[_personality_agent, _task_agent],
        instructions="""
            Talk to the user naturally and helpfully.
            Provide complete, well-formatted responses.
            When including mathematical expressions, use proper LaTeX formatting:
            - Use \\( expression \\) for inline math
            - Use \\[ expression \\] for display math (block equations)
            Do not mention delegation or other agents in your response.
        """,
        markdown=True,
    )

def parse_tasks_from_response(response_text):
    tasks = []
    for line in response_text.split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            task = line[2:].strip()
            if len(task) > 3:
                tasks.append({"text": task, "completed": False, "source": "extracted"})
    return tasks

if current_api_key and selected_model:
    personality_agent = create_personality_agent(provider_choice, selected_model, current_api_key)
    task_agent = create_task_agent(provider_choice, selected_model, current_api_key)
    main_agent = create_main_agent(provider_choice, selected_model, current_api_key, personality_agent, task_agent)

    st.title(f"🤖 AI Learning Assistant ({provider_choice} - {selected_model})")

    # Display chat history with LaTeX support
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            display_content_with_latex(
                message['content'], 
                st.session_state.get('selected_font', 'Arial')
            )

    if prompt := st.chat_input("You:"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            display_content_with_latex(
                prompt, 
                st.session_state.get('selected_font', 'Arial')
            )

        with st.chat_message("assistant"):
            try:
                message_placeholder = st.empty()
                full_prompt = f"Context from PDF:\n{pdf_text}\n\nUser: {prompt}" if pdf_text else prompt
                response = main_agent.run(full_prompt)
                content = response.content if hasattr(response, "content") else str(response)
                
                with message_placeholder.container():
                    display_content_with_latex(
                        content, 
                        st.session_state.get('selected_font', 'Arial')
                    )
                    
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
                content = "Sorry, I encountered an error processing your request."
                with message_placeholder.container():
                    display_content_with_latex(
                        content, 
                        st.session_state.get('selected_font', 'Arial')
                    )

            st.session_state.messages.append({"role": "assistant", "content": content})

        # Task extraction with LaTeX support
        try:
            task_response = task_agent.run(f"Extract tasks from this conversation: User said: '{prompt}'")
            task_content = task_response.content if hasattr(task_response, "content") else str(task_response)
            new_tasks = parse_tasks_from_response(task_content)
            for task in new_tasks:
                if task["text"].lower() not in [t["text"].lower() for t in st.session_state.tasks]:
                    st.session_state.tasks.append(task)
            if new_tasks:
                st.rerun()
        except Exception as e:
            st.error(f"Error in task extraction: {str(e)}")

        # Analysis sections with LaTeX support
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("🧠 Personality Analysis", expanded=False):
                try:
                    res = personality_agent.run(f"Analyze this conversation: User said: '{prompt}'")
                    analysis_content = res.content if hasattr(res, 'content') else str(res)
                    display_content_with_latex(
                        analysis_content,
                        st.session_state.get('selected_font', 'Arial')
                    )
                except Exception as e:
                    st.error(f"Error in personality analysis: {str(e)}")

        with col2:
            with st.expander("📋 Latest Task Analysis", expanded=False):
                try:
                    res = task_agent.run(f"Extract tasks from this conversation: User said: '{prompt}'")
                    task_analysis_content = res.content if hasattr(res, 'content') else str(res)
                    display_content_with_latex(
                        task_analysis_content,
                        st.session_state.get('selected_font', 'Arial')
                    )
                except Exception as e:
                    st.error(f"Error in task extraction: {str(e)}")
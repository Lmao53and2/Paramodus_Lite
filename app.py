import streamlit as st
from agno.agent import Agent
from agno.models.perplexity import Perplexity
from load_storage import load_session_storage, load_personality_storage, load_task_storage
from agno.document.reader.pdf_reader import PDFReader
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# API Key setup
pplx_api_key = os.getenv("PERPLEXITY_API_KEY")
if not pplx_api_key:
    st.warning("API key not found in .env file")
    pplx_api_key = st.text_input("Enter your API Key:")
    if pplx_api_key:
        os.environ["PERPLEXITY_API_KEY"] = pplx_api_key
else:
    st.success("All Activated, ask away :)")

if pplx_api_key:
    # PDF upload and extraction
    uploaded_pdf = st.file_uploader("Upload a PDF for context", type="pdf")
    pdf_text = ""
    if uploaded_pdf is not None:
        reader = PDFReader()
        with open("temp_uploaded.pdf", "wb") as f:
            f.write(uploaded_pdf.read())
        documents = reader.read("temp_uploaded.pdf")
        pdf_text = "\n".join([doc.content for doc in documents if doc.content])
        st.success("PDF loaded and text extracted!")

    # Create a sidebar for tasks
    with st.sidebar:
        st.header("📋 Task Manager")
        
        # Display current tasks
        if st.session_state.tasks:
            st.subheader("Current Tasks:")
            for i, task in enumerate(st.session_state.tasks):
                col1, col2 = st.columns([4, 1])
                with col1:
                    # Make tasks clickable checkboxes
                    completed = st.checkbox(task["text"], key=f"task_{i}", value=task.get("completed", False))
                    if completed != task.get("completed", False):
                        st.session_state.tasks[i]["completed"] = completed
                with col2:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.tasks.pop(i)
                        st.rerun()
        else:
            st.info("No tasks yet. Start chatting to extract tasks!")
        
        # Manual task addition
        st.subheader("Add Manual Task:")
        manual_task = st.text_input("Enter a task:", key="manual_task_input")
        if st.button("Add Task") and manual_task:
            st.session_state.tasks.append({
                "text": manual_task,
                "completed": False,
                "source": "manual"
            })
            st.rerun()
        
        # Clear all tasks button
        if st.session_state.tasks and st.button("Clear All Tasks"):
            st.session_state.tasks = []
            st.rerun()

        # Font selection (moved here)
        st.markdown("---")
        font_options = [
            "Arial", "Calibri", "Comic Sans MS", "Courier New", "Georgia", "Helvetica", "Times New Roman", "Trebuchet MS", "Verdana"
        ]
        selected_font = st.selectbox("Choose chat font", font_options, index=0, key="font_select")
        st.session_state.selected_font = selected_font
        st.markdown(f"""
            <style>
            html, body, [class^='st-'], .stChatMessage, .stMarkdown, .stText, .stExpander, .stTextInput, .stButton, .stSelectbox, .stTextArea, .stAlert {{
                font-family: '{selected_font}', sans-serif !important;
            }}
            </style>
        """, unsafe_allow_html=True)

    # Agent creation functions
    @st.cache_resource
    def create_personality_agent(api_key):
        return Agent(
            name="Personality Agent",
            role="Summarize the conversation and identify the user's personality traits.",
            model=Perplexity(id="sonar", api_key=api_key),
            add_history_to_messages=True,
            storage=load_personality_storage(),
            instructions="Summarize the conversation and give a brief personality analysis.",
            markdown=True,
            stream=False,
        )

    @st.cache_resource
    def create_task_agent(api_key):
        return Agent(
            name="Task Agent",
            role="Extract tasks from the conversation.",
            model=Perplexity(id="sonar", api_key=api_key),
            add_history_to_messages=True,
            storage=load_task_storage(),
            instructions="""
            Extract actionable tasks from the conversation. 
            Return tasks as a simple list, one task per line, starting with '- '.
            Focus on concrete, actionable items.
            """,
            markdown=True,
            stream=False,
        )

    @st.cache_resource
    def create_main_agent(api_key, _personality_agent, _task_agent):
        return Agent(
            name="Main Agent",
            role="Talk to the user and delegate to other agents.",
            model=Perplexity(id="sonar", api_key=api_key),
            add_history_to_messages=True,
            storage=load_session_storage(),
            team=[_personality_agent, _task_agent],
            instructions="""
            Talk to the user naturally and helpfully.
            Provide complete, well-formatted responses.
            Do not mention delegation or other agents in your response.
            """,
            markdown=True,
            stream=False,
        )

    # Function to parse tasks from agent response
    def parse_tasks_from_response(response_text):
        tasks = []
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                task_text = line[2:].strip()
                if task_text and len(task_text) > 3:  # Filter out very short items
                    tasks.append({
                        "text": task_text,
                        "completed": False,
                        "source": "extracted"
                    })
        return tasks

    # Initialize agents
    personality_agent = create_personality_agent(pplx_api_key)
    task_agent = create_task_agent(pplx_api_key)
    main_agent = create_main_agent(pplx_api_key, personality_agent, task_agent)

    # Main chat interface
    st.title("🤖 AI Learning Assistant")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{message['content']}</span>", unsafe_allow_html=True)

    # Chat input from user
    if prompt := st.chat_input("You:"):
        # Store only the user's actual message in chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display only the user's message, not the PDF content
        with st.chat_message("user"):
            st.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{prompt}</span>", unsafe_allow_html=True)

        # Combine PDF text with user prompt for agent processing (behind the scenes)
        combined_prompt = f"Context from PDF:\n{pdf_text}\n\nUser: {prompt}" if pdf_text else prompt

        # Get response using the combined prompt
        with st.chat_message("assistant"):
            try:
                message_placeholder = st.empty()
                response = main_agent.run(combined_prompt)

                # Handle different response types
                if hasattr(response, 'content'):
                    content = response.content
                elif isinstance(response, str):
                    content = response
                else:
                    content = str(response)

                # Clean up response if it contains RunResponse wrapper
                if content.startswith("RunResponse(content="):
                    match = re.search(r"content='([^']*)'", content)
                    if match:
                        content = match.group(1)
                    else:
                        content = content.split("content=", 1)[-1].strip("'\")")

                message_placeholder.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{content}</span>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
                content = "Sorry, I encountered an error processing your request."
                message_placeholder.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{content}</span>", unsafe_allow_html=True)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": content})

        # Extract and add new tasks automatically
        try:
            task_response = task_agent.run(
                f"Extract tasks from this conversation: User said: '{prompt}'"
            )
            if hasattr(task_response, 'content'):
                task_content = task_response.content
            else:
                task_content = str(task_response)
            
            # Parse tasks and add to session state
            new_tasks = parse_tasks_from_response(task_content)
            for new_task in new_tasks:
                # Check if task already exists to avoid duplicates
                existing_tasks = [task["text"].lower() for task in st.session_state.tasks]
                if new_task["text"].lower() not in existing_tasks:
                    st.session_state.tasks.append(new_task)
            
            if new_tasks:
                st.rerun()  # Refresh to show new tasks in sidebar
                
        except Exception as e:
            st.error(f"Error in task extraction: {str(e)}")

        # Show expandable sections for detailed analysis
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("🧠 Personality Analysis", expanded=False):
                try:
                    personality_response = personality_agent.run(
                        f"Analyze this conversation: User said: '{prompt}'"
                    )
                    if hasattr(personality_response, 'content'):
                        st.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{personality_response.content}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{str(personality_response)}</span>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error in personality analysis: {str(e)}")

        with col2:
            with st.expander("📋 Latest Task Analysis", expanded=False):
                try:
                    task_response = task_agent.run(
                        f"Extract tasks from this conversation: User said: '{prompt}'"
                    )
                    if hasattr(task_response, 'content'):
                        st.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{task_response.content}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='font-family:{st.session_state.get('selected_font', 'Arial')},sans-serif'>{str(task_response)}</span>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error in task extraction: {str(e)}")
    # ...existing code...

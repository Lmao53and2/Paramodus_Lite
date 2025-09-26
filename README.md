
# Paragomus Lite

A multi-agent, AI-powered productivity assistant built with Streamlit and the Agno framework. It enables learning, task extraction, and personality profiling through interactive conversation. Paragomus Lite supports PDF ingestion for context and integrates with Perplexity, Groq, and OpenAI.

---

## Features

- Integration with multiple LLM providers: Perplexity, Groq, OpenAI  
- Context input by uploading PDFs  
- Personality analysis agent  
- Automated and manual task extraction and tracking  
- Streamlit-powered chat UI with customizable fonts  
- Persistent memory using SQLite databases  

> **Caution:**  
> - Font changer may interrupt chat flow  
> - In-progress UI elements (fonts, LLM changer) may exhibit visual bugs  

---

## Roadmap (Future Features)

- Decouple logic from Streamlit to deliver an installable version  
- Make personality agent adapt dynamically during conversations  
- Limit visible tasks for better clarity  
- Add advanced UI customization options  

---

## Installation

### Clone the Repository
```bash
git clone https://github.com/Lmao53and2/Paramodus_Lite.git
cd Paramodus_Lite
````

### Set Up Environment Variables

Create a `.env` file in the project root:

```env
PERPLEXITY_API_KEY=your-perplexity-api-key
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key

# Optional: Customize SQLite storage paths
AGENT_STORAGE_PATH=business_agent.db
PERSONALITY_STORAGE_PATH=personality_data.db
TASK_STORAGE_PATH=task_data.db
```

### Install Dependencies

```bash
uv sync
```

### Run the App

With `uv` (recommended):

```bash
uv run app.py
```

Alternatively, directly using Streamlit:

```bash
streamlit run app.py
```

---

## Usage Guide

1. Select your preferred API provider and model via the sidebar.
2. Upload a PDF to provide context for the conversation.
3. Type your message in the chat input field.
4. View task and personality analysis in expandable sections.
5. Use the sidebar to add or manage tasks.

---

## Platform Notes

Ensure you have `git`, Python 3, and `uv` installed before proceeding:

* **macOS:** Requires `git`, Python 3, and `uv`
* **Ubuntu:** Requires `git`, `python3`, and `uv`
* **Windows (PowerShell):** Requires `git`, Python (3.x), and `uv`

---

## License

Licensed under the MIT License.




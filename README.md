# ProductAI

ProductAI is a multi-agent AI powered, general productivity assistant by Streamlit and the Agno framework, designed to facilitate learning, task extraction, and personality analysis through conversational interaction. It supports context ingestion from uploaded PDFs and integrates with leading LLM providers including Perplexity, Groq, and OpenAI.

## Features

* 🔄 Multi-provider LLM support (Perplexity, Groq, OpenAI)
* 📄 PDF ingestion for contextual grounding
* 🧠 Personality profiling agent
* 📋 Automated and manual task extraction and tracking
* 💬 Interactive Streamlit chat UI with customizable fonts
* 💾 Persistent agent memory using SQLite

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/73IA/ProductAI_1.git
cd ProductAI_1
```

### 2. Set Up Environment Variables

Create a `.env` file with your API keys:

```env
PERPLEXITY_API_KEY=your-perplexity-api-key
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
```

Optional overrides for SQLite file paths:

```env
AGENT_STORAGE_PATH=business_agent.db
PERSONALITY_STORAGE_PATH=personality_data.db
TASK_STORAGE_PATH=task_data.db
```

### 3. Install Dependencies

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management:

```bash
uv sync
```

## Running the Application

Start the Streamlit app:

```bash
uv run app.py
```

Or directly:

```bash
streamlit run app.py
```

## Usage

1. Configure your API provider and select a model via the sidebar.
2. Upload a PDF file to use its contents as conversation context.
3. Start chatting in the input box below the messages.
4. View personality and task analysis from conversation in expandable sections.
5. Add or manage tasks in the sidebar.

## Platform Notes

| OS      | Command Line Tools Required      |
| ------- | -------------------------------- |
| macOS   | git, Python 3, uv                |
| Ubuntu  | git, python3, uv                 |
| Windows | git, python, uv (via PowerShell) |

## License

MIT

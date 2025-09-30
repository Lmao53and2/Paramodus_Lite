# Paramodus AI Assistant

A clean, modern AI assistant built with Agno v2.0 and Streamlit.

## Features

- 🤖 Multi-provider AI support (OpenAI, Groq, Perplexity)
- 💬 Conversation history with persistent storage
- ⚙️ Easy provider and model switching
- 🎨 Clean, modern interface

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Lmao53and2/Paramodus_Lite.git
cd Paramodus_Lite

# Install dependencies
pip install -r requirements_new.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
```

Get your API keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **Groq**: https://console.groq.com/
- **Perplexity**: https://www.perplexity.ai/

### 3. Run the Application

```bash
streamlit run app_new.py
```

## Usage

1. Select your preferred AI provider from the sidebar
2. Choose a model
3. Start chatting with your AI assistant
4. Conversation history is automatically saved

## Architecture

- **Frontend**: Streamlit for the web interface
- **AI Framework**: Agno v2.0 for agent management
- **Database**: SQLite for conversation storage
- **Models**: Support for multiple AI providers

## Development

This is a clean, minimal implementation perfect for:
- Learning Agno v2.0 patterns
- Building custom AI assistant features
- Client project foundations

## Business Applications

Ideal foundation for:
- Customer service bots
- Personal productivity assistants
- Educational tutoring systems
- Creative writing aids
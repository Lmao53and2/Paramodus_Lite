# Paramodus Lite

A high-performance, multi-agent AI productivity assistant built with **Agno v2.0** and **Streamlit**. Designed for learning, task extraction, and context-aware research.

---

## 🚀 Features

- **Multi-Provider Support**: Switch between **OpenAI**, **Groq**, and **Perplexity** seamlessly.
- **Contextual PDF Ingestion**: Upload documents to give the AI project-specific knowledge.
- **Agentic Task Extraction**: Automatically identifies actionable items from your conversation.
- **Personality Profiling**: Analyzes interaction patterns for personalized assistance.
- **Persistent Memory**: SQLite-backed storage for long-term project tracking.
- **Math Ready**: Full support for LaTeX rendering ($inline$ and $$block$$).

---

## 🛠️ Installation

### 1. Clone & Setup
```bash
git clone https://github.com/Lmao53and2/Paramodus_Lite.git
cd Paramodus_Lite
```

### 2. Configure Environment
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Edit `.env` with your API keys:
- [OpenAI Dashboard](https://platform.openai.com/)
- [Groq Console](https://console.groq.com/)
- [Perplexity API](https://www.perplexity.ai/settings/api)

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
streamlit run app.py
```

---

## 📁 Project Structure

- `app.py`: Main Streamlit interface and Agent orchestration.
- `load_storage.py`: SQLite storage configurations for persistent memory.
- `.env.example`: Template for required API keys.
- `requirements.txt`: Pinned production dependencies.

---

## ⚠️ Notes
- Ensure your `.env` file is never committed (checked by `.gitignore`).
- SQLite databases (`*.db`) are stored locally in the project root.
- PDF uploads use temporary processing to ensure privacy and performance.

---

## 📜 License
MIT License - See [LICENSE](LICENSE) for details.

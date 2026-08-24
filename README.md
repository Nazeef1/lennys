# The Lenny Growth Assistant 🚀
> Full-Stack, AI-Powered Conversational Web Application & Content Generator Grounded in Lenny's Podcast & Newsletter Transcripts.

---

## 📌 Executive Summary

**The Lenny Growth Assistant** is a forward-deployed AI platform designed for product managers, growth leaders, and executive teams. It ingests the complete transcript corpus of Lenny's Podcast and Newsletter, providing:
1. **Grounded RAG Conversational Strategy**: Accurate answers strictly cited from guest interviews and newsletters with interactive citation accordions.
2. **Ship 30 for 30 Content Skill**: Dedicated skill tool generating ~1,250-word masterclass essays with hooks, narrative progression, skimmable typography, and actionable takeaways.
3. **Side-by-Side Sandboxed Artifact Viewer**: Native rendering of generated interactive HTML growth calculators and Markdown reports inside an isolated iframe sandbox (`sandbox="allow-scripts"`).
4. **Flexible Multi-LLM Provider Switcher**: Runtime dynamic toggling between **Ollama (Local)**, **Anthropic Claude 3.5 Sonnet**, **OpenAI GPT-4o**, and an **Auto-Resilience Fallback Engine**.

---

## 🏗 System Architecture Overview

```
                                  +-----------------------+
                                  |   REACT VITE UI       |
                                  | (Split Pane View)     |
                                  +-----------+-----------+
                                              | REST API
                                  +-----------v-----------+
                                  |   FASTAPI BACKEND     |
                                  +-----+-----------+-----+
                                        |           |
            +---------------------------v---+   +---v---------------------------+
            |      LENNY AGENT CORE         |   |      HYBRID RAG ENGINE         |
            | - Intent Classifier           |   | - Markdown Metadata Extractor |
            | - Ship 30 Essay Skill         |   | - Semantic Paragraph Chunker  |
            | - Artifact Generator Tool     |   | - TF-IDF / Vector Search      |
            +---------------+---------------+   +-------------------------------+
                            |
            +---------------v---------------+
            |    DYNAMIC LLM REGISTRY       |
            | - Ollama (llama3.2 local)     |
            | - Anthropic Claude 3.5 Sonnet |
            | - OpenAI GPT-4o               |
            | - Resilience Fallback Engine  |
            +-------------------------------+
```

---

## ⚡ Quickstart Guide (One-Command Launch)

### Option A: Local Run (Recommended for Evaluators)
Ensure Python 3.11+ and Node.js v18+ are installed.

```bash
# 1. Clone the repository & enter workspace
git clone https://github.com/your-username/lenny-growth-assistant.git
cd lenny-growth-assistant

# 2. Run single-command launcher
python run.py
```
`run.py` will automatically:
- Install frontend npm dependencies.
- Initialize database schemas (`SQLite` zero-config database).
- Index Lenny's Podcast transcripts into the vector store.
- Launch the FastAPI Backend on `http://localhost:8000`.
- Launch the React Vite Frontend on `http://localhost:3000`.

Open your browser to **`http://localhost:3000`** to evaluate the application!

---

### Option B: Docker Compose (Production Setup)
To run with PostgreSQL containerization:

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## ⚙️ Environment Variables & Model Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Description | Default | Required? |
| :--- | :--- | :--- | :--- |
| `DEFAULT_PROVIDER` | Active LLM model provider (`ollama`, `anthropic`, `openai`, `fallback`) | `ollama` | Yes |
| `OLLAMA_BASE_URL` | Ollama HTTP endpoint | `http://localhost:11434` | If using Ollama |
| `OLLAMA_MODEL` | Local Ollama model name | `llama3.2` | If using Ollama |
| `ANTHROPIC_API_KEY` | Anthropic Claude API Key | `sk-ant-...` | Optional |
| `OPENAI_API_KEY` | OpenAI API Key | `sk-...` | Optional |
| `DATABASE_URL` | SQLAlchemy Connection URL | `sqlite:///./lenny_assistant.db` | Yes |

### 🤖 Local Model Setup (Ollama)
To run Ollama locally for the demo:
1. Install Ollama from [ollama.com](https://ollama.com).
2. Pull your preferred model:
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama daemon: `ollama serve`.
4. Switch to **Ollama** in the UI header dropdown!

> **Resilience Fallback Note**: If Ollama or cloud API keys are missing/unreachable on your test machine, the application **automatically uses the Resilience Fallback Engine**. The system remains 100% operational and interactive without crashing.

---

## 🧪 Automated Testing & QA Verification

### Automated Unit Tests
Run the comprehensive Pytest suite covering API endpoints, RAG chunking, LLM provider switching, and persistence:

```bash
python -m pytest tests/
```

Expected Output:
```text
======================== 7 passed in 6.64s =========================
```

### Manual Test Matrix
See [tests/manual_test_plan.md](file:///c:/Users/HP/Desktop/lennys/tests/manual_test_plan.md) for step-by-step UI evaluation steps.

---

## 📁 Repository Structure

```text
lenny-growth-assistant/
├── PRD.md                       # Product Requirements Document & Forward Deployment Brief
├── design.md                    # UI/UX principles, layout specs, and security isolation
├── architecture.md              # System topology, database schema, RAG & LLM specs
├── README.md                    # Main project documentation & quickstart
├── run.py                       # Single-command local runner script
├── docker-compose.yml           # Production Docker setup with PostgreSQL
├── .env.example                 # Environment configuration template
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application entrypoint
│       ├── config.py            # App settings and environment loader
│       ├── db/                  # Database models & connection pool
│       ├── llm/                 # Dynamic LLM provider registry (Claude, OpenAI, Ollama, Fallback)
│       ├── rag/                 # Transcript chunking, TF-IDF vector indexing & retrieval
│       ├── skills/              # Ship 30 for 30 essay generation skill
│       ├── agent/               # Agent orchestrator & intent classifier
│       └── api/                 # REST API endpoints
├── frontend/
│   ├── index.html               # Main HTML entrypoint
│   ├── src/                     # React components (Header, Sidebar, Chat, Sandboxed Viewer)
│   └── vite.config.js           # Vite development server & API proxy
├── data/
│   ├── fetch_transcripts.py     # Script to sync Lenny podcast transcripts
│   └── transcripts/             # Bundled podcast & newsletter Markdown transcripts
├── agent_transcripts/
│   └── transcript_log.json      # Agent execution logs, decision traces & recovery logs
└── tests/                       # Pytest test suite & manual test plan
```

---

## 🔒 Security Isolation Strategy
Generated HTML artifacts are treated as untrusted user content. They are rendered inside the **Artifact Viewer** using an `<iframe>` sandbox:
```html
<iframe srcDoc={content} sandbox="allow-scripts" />
```
This grants script execution for interactive calculators while enforcing a null-origin sandbox that blocks parent DOM manipulation, cookie access, and top-level redirection.

---

## 🤝 Evaluator Handoff & Maintenance
- **Refreshing Knowledge Base**: Run `python data/fetch_transcripts.py` to sync new podcasts/newsletters.
- **Logs & Observability**: Backend outputs structured logs detailing query intent, retrieval scores, active provider execution, and fallback events.

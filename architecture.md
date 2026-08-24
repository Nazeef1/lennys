# System Architecture Specification
## The Lenny Growth Assistant

---

## 1. System Topology & Component Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React + Vite + Tailwind)                    │
│   Header (Model Selector) │ Sidebar (Sessions) │ Chat Pane │ Artifact Viewer    │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │ HTTP / REST API (Port 8000)
┌────────────────────────────────────────▼────────────────────────────────────────┐
│                             BACKEND (FastAPI Core)                              │
│   ├── /api/chat            ├── /api/sessions           ├── /api/models          │
│   └── /api/transcripts     └── /api/artifacts          └── /api/health          │
└──────────┬─────────────────────────────┬──────────────────────────┬─────────────┘
           │                             │                          │
┌──────────▼───────────┐    ┌────────────▼───────────┐    ┌─────────▼───────────┐
│   LENNY AGENT CORE   │    │     HYBRID RAG         │    │ DYNAMIC LLM LAYER   │
│ - Intent Detection   │◄───┤ - Markdown Parsing     │    │ - Ollama (Local)    │
│ - Ship 30 Skill      │    │ - Semantic Chunking    │───►│ - Anthropic Claude  │
│ - Artifact Extractor │    │ - TF-IDF Vector Search │    │ - OpenAI GPT-4o     │
└──────────┬───────────┘    └────────────────────────┘    │ - Resilience Engine │
           │                                              └─────────────────────┘
┌──────────▼───────────┐
│   PERSISTENCE LAYER  │
│ - PostgreSQL (Prod)  │
│ - SQLite (Fallback)  │
└──────────────────────┘
```

---

## 2. Database Schema (SQLAlchemy ORM)

### 2.1 Entity Relationship Diagram
```
┌───────────────────────────┐       ┌───────────────────────────┐
│         sessions          │       │         messages          │
├───────────────────────────┤       ├───────────────────────────┤
│ id (PK, String)           │1    * │ id (PK, String)           │
│ title (String)            ├───────┤ session_id (FK, String)   │
│ active_provider (String)  │       │ role (user/assistant)     │
│ created_at (DateTime)     │       │ content (Text)            │
│ updated_at (DateTime)     │       │ citations (JSON List)     │
└─────────────┬─────────────┘       │ artifact_id (String, Null)│
              │ 1                   │ created_at (DateTime)     │
              │                     └───────────────────────────┘
              │ *
┌─────────────▼─────────────┐
│         artifacts         │
├───────────────────────────┤
│ id (PK, String)           │
│ session_id (FK, String)   │
│ title (String)            │
│ artifact_type (html/md)   │
│ content (Text)            │
│ security_metadata (JSON)  │
│ created_at (DateTime)     │
└───────────────────────────┘
```

---

## 3. RAG Retrieval & Ingestion Pipeline

### 3.1 Document Ingestion Flow
1. **Directory Scanner**: `RAGEngine` scans `data/transcripts/` for Markdown files on startup.
2. **Metadata Extractor**: Reads frontmatter to extract `title`, `date`, `guest`, and `post_url`.
3. **Semantic Chunking**: Paragraphs are chunked into 700-character windows with 150-character sliding overlap.
4. **Vector Matrix Construction**: Converts chunk text corpus into TF-IDF vector matrix (`TfidfVectorizer(stop_words='english', ngram_range=(1,2))`).

### 3.2 Hybrid Search Strategy
When a query arrives:
1. Transforms query string into vector space representation.
2. Computes Cosine Similarity against all index chunks.
3. Ranks matches by score and filters top-5 results above score threshold.
4. Formats citation objects containing source metadata and quotes.

---

## 4. LLM Switcher & Resilience Architecture

### 4.1 Dynamic Provider Switcher
`ProviderRegistry` exposes a uniform interface (`BaseLLMProvider` abstract class) with support for:
- `OllamaProvider`: Connects to `http://localhost:11434/api/chat`.
- `AnthropicProvider`: Connects to Claude 3.5 Sonnet API via `anthropic` SDK.
- `OpenAIProvider`: Connects to GPT-4o API via `openai` SDK.
- `FallbackProvider`: Local mock resilience engine when external services are unreachable.

### 4.2 Resilience Fallback Cascade
```
User Request ──► Active Provider (e.g. Ollama)
                       │
             Success? ─┼──► Return Response
                       │ (Failure / Timeout)
                       ▼
             Resilience Fallback Engine ──► Grounded Response with Diagnostics
```

---

## 5. REST API Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health status, active provider, and chunk count. |
| `POST` | `/api/sessions` | Create new growth consultation session. |
| `GET` | `/api/sessions` | List all historical sessions. |
| `GET` | `/api/sessions/{id}/messages` | Retrieve session messages and citations. |
| `POST` | `/api/chat` | Send prompt to Lenny Agent. |
| `GET` | `/api/models` | List providers and availability status. |
| `POST` | `/api/models/select` | Toggle active model provider. |
| `POST` | `/api/transcripts/ingest` | Trigger or refresh knowledge index. |
| `GET` | `/api/artifacts/{id}` | Retrieve generated artifact code and security metadata. |

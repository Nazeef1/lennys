# System Architecture Specification
## The Lenny Growth Assistant

---

## 1. System Topology & Component Boundaries

```mermaid
graph TD
    Client[React Frontend / Browser] -->|REST API Requests| API[FastAPI Core Server]
    API -->|Intent & Session Data| Agent[Lenny Growth Agent Core]
    Agent -->|Query Vector Search| RAG[Hybrid RAG Engine]
    RAG -->|Read Markdown Transcripts| Corpus[(Transcript Corpus)]
    Agent -->|Execute Prompt| LLM[Dynamic Provider Registry]
    LLM -->|Local| Ollama[Ollama Local LLM]
    LLM -->|Cloud| Claude[Anthropic Claude API]
    LLM -->|Cloud| OpenAI[OpenAI GPT-4o API]
    LLM -->|Fallback| Resilience[Resilience Fallback Engine]
    Agent -->|Persist History & Artifacts| DB[(SQLite / PostgreSQL DB)]
```

---

## 2. Dynamic Sequence Diagrams

### 2.1 Intent Routing & RAG Search Flow
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as React Frontend
    participant API as FastAPI Router
    participant Agent as Lenny Growth Agent
    participant RAG as RAG Engine
    participant LLM as LLM Provider

    User->>UI: Submits query ("Write Ship 30 essay on PLG")
    UI->>API: POST /api/chat (session_id, prompt)
    API->>Agent: execute(session_id, prompt)
    Agent->>RAG: search(query, top_k=5)
    RAG-->>Agent: Returns Ranked Chunks & Guest Metadata
    Agent->>Agent: Intent Classifier -> Ship30EssayTool
    Agent->>LLM: generate_response(Ship30Prompt, Context)
    LLM-->>Agent: Returns 1,250-Word Grounded Essay
    Agent->>API: Persists message & citations
    API-->>UI: Streams response + Citations Accordion
```

### 2.2 LLM Resilience Fallback Cascade
```mermaid
sequenceDiagram
    autonumber
    participant Agent as Agent Core
    participant Registry as Provider Registry
    participant Ollama as Ollama Daemon
    participant Fallback as Resilience Engine

    Agent->>Registry: Request Active Provider (Ollama)
    Registry->>Ollama: POST http://localhost:11434/api/chat
    alt Ollama Available
        Ollama-->>Registry: Returns Model Output
        Registry-->>Agent: Success Response
    else Connection Timeout / Missing Daemon
        Ollama--xRegistry: 500 / Connection Error
        Registry->>Fallback: Trigger Resilience Engine
        Fallback-->>Registry: Returns Grounded Knowledge Response
        Registry-->>Agent: Serves Fallback Response with Diagnostic Logs
    end
```

---

## 3. Database Schema (SQLAlchemy ORM)

### 3.1 Entity Relationship Diagram
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

## 4. RAG Retrieval & Ingestion Pipeline

### 4.1 Document Ingestion Flow
1. **Directory Scanner**: `RAGEngine` scans `data/transcripts/` for Markdown files on startup.
2. **Metadata Extractor**: Reads frontmatter to extract `title`, `date`, `guest`, and `post_url`.
3. **Semantic Chunking**: Paragraphs are chunked into 700-character windows with 150-character sliding overlap.
4. **Vector Matrix Construction**: Converts chunk text corpus into TF-IDF vector matrix (`TfidfVectorizer(stop_words='english', ngram_range=(1,2))`).

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

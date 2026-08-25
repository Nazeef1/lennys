import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    API_V1_STR: str = "/api"
    
    # LLM Keys & Endpoints
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    DEFAULT_PROVIDER: str = "fallback"  # ollama, anthropic, openai, fallback
    
    # Database (Use /tmp for Vercel/serverless writable SQLite)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:////tmp/lenny_assistant.db" if os.getenv("VERCEL") else "sqlite:///./lenny_assistant.db")

    @property
    def sanitized_database_url(self) -> str:
        url = self.DATABASE_URL
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    TRANSCRIPT_DIR: str = os.path.join(DATA_DIR, "transcripts")
    VECTOR_DB_DIR: str = os.path.join(DATA_DIR, "vector_db")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

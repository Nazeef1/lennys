import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.db.database import init_db
from backend.app.rag.engine import rag_engine
from backend.app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lenny_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing The Lenny Growth Assistant Database...")
    init_db()
    
    logger.info("Indexing Lenny's Podcast Transcripts for RAG...")
    chunk_count = rag_engine.build_index()
    logger.info(f"RAG Indexing complete. Indexed {chunk_count} chunks.")
    
    yield
    logger.info("Shutting down The Lenny Growth Assistant Application.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Conversational AI Assistant grounded in Lenny's Podcast and Newsletter Transcripts.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. The resilience engine has logged details."}
    )

# Include Router with and without /api prefix for Vercel rewrite compatibility
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

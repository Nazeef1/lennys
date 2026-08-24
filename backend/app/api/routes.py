import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import SessionModel, MessageModel, ArtifactModel
from backend.app.llm.provider import provider_registry
from backend.app.rag.engine import rag_engine
from backend.app.agent.core import agent
from backend.app.skills.ship30for30 import Ship30For30Skill

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Schemas
class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Growth Consultation"

class ChatRequest(BaseModel):
    session_id: str
    message: str
    provider: Optional[str] = None

class SelectModelRequest(BaseModel):
    provider: str

# Endpoints

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "indexed_chunks": len(rag_engine.chunks),
        "is_indexed": rag_engine.is_indexed,
        "active_provider": provider_registry.active_provider_name
    }

@router.post("/sessions")
def create_session(req: CreateSessionRequest, db: Session = Depends(get_db)):
    session_obj = SessionModel(
        title=req.title,
        active_provider=provider_registry.active_provider_name
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return {
        "id": session_obj.id,
        "title": session_obj.title,
        "active_provider": session_obj.active_provider,
        "created_at": session_obj.created_at.isoformat()
    }

@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "active_provider": s.active_provider,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        } for s in sessions
    ]

@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(MessageModel.created_at.asc()).all()
    
    result = []
    for m in messages:
        art_dict = None
        if m.artifact_id:
            art_obj = db.query(ArtifactModel).filter(ArtifactModel.id == m.artifact_id).first()
            if art_obj:
                art_dict = {
                    "id": art_obj.id,
                    "title": art_obj.title,
                    "type": art_obj.artifact_type,
                    "content": art_obj.content
                }
        result.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "citations": m.citations or [],
            "artifact": art_dict,
            "created_at": m.created_at.isoformat()
        })
    return result

@router.post("/chat")
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty")
    
    response_data = await agent.execute(
        db=db,
        session_id=req.session_id,
        user_message=req.message,
        provider_name=req.provider
    )
    return response_data

@router.get("/models")
async def get_models():
    providers = await provider_registry.list_providers_status()
    return {
        "active": provider_registry.active_provider_name,
        "providers": providers
    }

@router.post("/models/select")
def select_model(req: SelectModelRequest):
    success = provider_registry.set_active_provider(req.provider)
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid provider '{req.provider}'")
    return {"status": "success", "active_provider": provider_registry.active_provider_name}

@router.post("/transcripts/ingest")
def trigger_ingest():
    chunk_count = rag_engine.build_index()
    return {
        "status": "success",
        "chunks_indexed": chunk_count
    }

@router.get("/transcripts/status")
def transcript_status():
    return {
        "transcript_dir": rag_engine.transcript_dir,
        "indexed_chunks": len(rag_engine.chunks),
        "is_indexed": rag_engine.is_indexed
    }

@router.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    art_obj = db.query(ArtifactModel).filter(ArtifactModel.id == artifact_id).first()
    if not art_obj:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {
        "id": art_obj.id,
        "session_id": art_obj.session_id,
        "title": art_obj.title,
        "type": art_obj.artifact_type,
        "content": art_obj.content,
        "security_metadata": art_obj.security_metadata,
        "created_at": art_obj.created_at.isoformat()
    }

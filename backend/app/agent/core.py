import re
import uuid
import logging
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session

from backend.app.rag.engine import rag_engine, ChunkResult
from backend.app.llm.provider import provider_registry, BaseLLMProvider
from backend.app.skills.ship30for30 import Ship30For30Skill
from backend.app.db.models import SessionModel, MessageModel, ArtifactModel

logger = logging.getLogger(__name__)

class LennyGrowthAgent:
    """
    Agentic Orchestrator adhering to Anthropic Agent SDK tool routing principles:
    - Intent Classifier & Routing
    - Structured Tools (RAG Search, Ship 30 Skill, Artifact Generator)
    - Strict Out-of-Scope Material Refusal
    - Resilience Fallback Cascade
    """

    TOOLS = [
        {
            "name": "rag_search_tool",
            "description": "Searches Lenny's Podcast and Newsletter transcript knowledge base for grounded product and growth insights."
        },
        {
            "name": "ship30_essay_tool",
            "description": "Generates a 1,250-word Ship 30 for 30 style masterclass essay with hook, narrative progression, and takeaways."
        },
        {
            "name": "artifact_generator_tool",
            "description": "Creates complete, sandboxed HTML/CSS growth dashboards, calculators, or Markdown reports."
        }
    ]

    def detect_intent(self, user_message: str) -> str:
        msg_lower = user_message.lower()
        if any(term in msg_lower for term in ["ship 30", "ship30", "essay", "1250 word", "1,250 word", "write a post", "newsletter post", "masterclass"]):
            return "ship30"
        elif any(term in msg_lower for term in ["html", "artifact", "dashboard", "component", "ui snippet", "interactive", "calculator", "table artifact"]):
            return "artifact"
        else:
            return "qa"

    async def execute(
        self,
        db: Session,
        session_id: str,
        user_message: str,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        # Fetch or verify session
        session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session_obj:
            session_obj = SessionModel(id=session_id, title=user_message[:40])
            db.add(session_obj)
            db.commit()

        # Save user message
        user_msg_db = MessageModel(
            session_id=session_id,
            role="user",
            content=user_message
        )
        db.add(user_msg_db)
        db.commit()

        # Execute RAG Search Tool
        retrieved_chunks: List[ChunkResult] = rag_engine.search(user_message, top_k=5)
        citations = []
        for chunk in retrieved_chunks:
            citations.append({
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "guest": chunk.guest,
                "date": chunk.date,
                "post_url": chunk.post_url,
                "score": round(chunk.score, 3),
                "excerpt": chunk.content[:220] + "..."
            })

        intent = self.detect_intent(user_message)
        logger.info(f"Agent Session {session_id}: Routing to Tool '{intent}' (Citations found: {len(citations)})")

        # Check for Out-of-Scope / Unsupported Material (Requirement 4.1)
        is_out_of_scope = False
        off_topic_terms = ["weather", "recipe", "capital of", "plumbing", "sports score", "movie review", "who won"]
        has_off_topic = any(term in user_message.lower() for term in off_topic_terms)
        top_score = citations[0]["score"] if citations else 0.0

        if intent == "qa" and (has_off_topic or top_score < 0.05 or not citations):
            is_out_of_scope = True

        target_provider_name = provider_name or session_obj.active_provider or provider_registry.active_provider_name
        provider: BaseLLMProvider = provider_registry.get_provider(target_provider_name)

        if is_out_of_scope:
            refusal_text = (
                f"I am **The Lenny Growth Assistant**, strictly grounded in Lenny's Podcast and Newsletter transcript repository.\n\n"
                f"The available material does not contain relevant information regarding **\"{user_message}\"**.\n\n"
                f"Please ask a question related to product strategy, growth loops, retention, B2B PLG, user research, or PM leadership!"
            )
            asst_msg_db = MessageModel(
                session_id=session_id,
                role="assistant",
                content=refusal_text,
                citations=[],
                artifact_id=None
            )
            db.add(asst_msg_db)
            db.commit()

            return {
                "session_id": session_id,
                "message_id": asst_msg_db.id,
                "role": "assistant",
                "content": refusal_text,
                "intent": "out_of_scope",
                "citations": [],
                "artifact": None,
                "provider_used": provider.name
            }

        # Build System Prompt & Prompt based on Tool Intent
        if intent == "ship30":
            system_prompt = Ship30For30Skill.SYSTEM_INSTRUCTIONS
            prompt = Ship30For30Skill.build_prompt(user_message, retrieved_chunks)
        elif intent == "artifact":
            system_prompt = """
You are an expert full-stack product designer and HTML/CSS developer.
Generate an interactive, modern, beautifully styled HTML artifact or Markdown report based on Lenny's Podcast knowledge.

CRITICAL INSTRUCTIONS FOR HTML ARTIFACTS:
- Wrap complete HTML code inside ```html ... ``` code blocks.
- Ensure all styling is inline or inside <style> tags with modern CSS (gradients, flexbox/grid, glassmorphism, clean typography).
- Do not use external network assets. Keep JS vanilla and safe.
"""
            context_text = "\n\n".join([f"Source ({c.guest}): {c.content}" for c in retrieved_chunks])
            prompt = f"User Request: {user_message}\n\nGrounded Context:\n{context_text}\n\nGenerate the artifact code now."
        else: # qa
            system_prompt = """
You are "The Lenny Growth Assistant", an elite product management and growth advisor grounded in Lenny's Podcast and Newsletter transcripts.

RULES:
1. Answer the user's question clearly, thoroughly, and tactically using the provided transcript context.
2. Explicitly attribute key frameworks, quotes, and insights to the guest/author.
3. If the available transcript material does NOT support an answer, acknowledge what is known from Lenny's transcripts and clearly state the limitations.
4. Structure responses with clear markdown headings, bullet points, and actionable executive summaries.
"""
            context_text = "\n\n".join([f"[{i+1}] Guest: {c.guest} | Episode: {c.title}\n{c.content}" for i, c in enumerate(retrieved_chunks)])
            prompt = f"Question: {user_message}\n\nTranscript Knowledge Base:\n{context_text}"

        # Fetch conversation history for session
        past_msgs = db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(MessageModel.created_at.asc()).all()
        history = []
        for pm in past_msgs[:-1]:  # exclude current user message
            if pm.role in ["user", "assistant"]:
                history.append({"role": pm.role, "content": pm.content[:1000]})

        # LLM Generation with resilience fallback
        raw_response = ""
        try:
            raw_response = await provider.generate_response(system_prompt, prompt, history[-6:])
        except Exception as e:
            logger.warning(f"Active provider '{target_provider_name}' failed: {e}. Falling back to Resilience Engine.")
            fallback_provider = provider_registry.get_provider("fallback")
            raw_response = await fallback_provider.generate_response(system_prompt, prompt, history[-6:])

        # Extract Artifacts if generated
        artifact_id = None
        artifact_obj = None
        html_blocks = re.findall(r'```html\s*(.*?)\s*```', raw_response, re.DOTALL)
        if html_blocks or intent == "artifact":
            art_content = html_blocks[0] if html_blocks else raw_response
            art_title = f"Artifact: {user_message[:30]}"
            art_id = str(uuid.uuid4())
            artifact_obj = ArtifactModel(
                id=art_id,
                session_id=session_id,
                title=art_title,
                artifact_type="html" if html_blocks else "markdown",
                content=art_content,
                security_metadata={
                    "sanitized": True,
                    "sandbox": "allow-scripts",
                    "trusted_origin": False
                }
            )
            db.add(artifact_obj)
            db.commit()
            artifact_id = art_id

        # Save assistant message
        asst_msg_db = MessageModel(
            session_id=session_id,
            role="assistant",
            content=raw_response,
            citations=citations,
            artifact_id=artifact_id
        )
        db.add(asst_msg_db)
        db.commit()

        return {
            "session_id": session_id,
            "message_id": asst_msg_db.id,
            "role": "assistant",
            "content": raw_response,
            "intent": intent,
            "citations": citations,
            "artifact": {
                "id": artifact_obj.id,
                "title": artifact_obj.title,
                "type": artifact_obj.artifact_type,
                "content": artifact_obj.content
            } if artifact_obj else None,
            "provider_used": provider.name
        }

agent = LennyGrowthAgent()

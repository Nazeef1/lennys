import logging
from typing import List, Dict, Any
from backend.app.rag.engine import ChunkResult

logger = logging.getLogger(__name__)

class Ship30For30Skill:
    """
    Dedicated skill encoding Ship 30 for 30 writing methodology:
    - Target length: ~1,250 words
    - Compelling hook & narrative arc
    - Skimmable typography (H2s, H3s, bullet points, bold emphasis)
    - Actionable takeaway framework
    - Grounded transcript citations
    """
    
    SYSTEM_INSTRUCTIONS = """
You are a master product strategist and growth writer trained in the Ship 30 for 30 digital writing methodology.
Your objective is to turn raw transcript insights into an authoritative, highly skimmable 1,250-word masterclass essay.

Follow these strict structural guidelines:

1. THE HOOK (100-150 words):
   - Open with an unconventional truth or sharp observation about modern product management/growth.
   - Clearly define the high-stakes problem PMs face today.
   - State what the reader will learn by the end of this essay.

2. THE NARRATIVE & DEEP INSIGHTS (400-500 words):
   - Frame the core philosophy based strictly on the provided transcript knowledge.
   - Use bold emphasis on key phrases for skimmability.
   - Integrate direct quotes and perspectives from Lenny's guests.

3. THE ACTIONABLE FRAMEWORK (400-500 words):
   - Break down the solution into a step-by-step 3-4 pillar framework.
   - Use clear bullet points, callout summaries, and tactical steps.
   - Provide concrete examples of how top teams apply this framework.

4. THE PLAYBOOK CHECKLIST & TAKEAWAY (150-200 words):
   - Provide a 5-step key takeaway checklist that readers can apply immediately.
   - End with a memorable closing thesis.

5. GROUNDING & CITATIONS:
   - Cite transcript sources explicitly (Guest, Episode/Post, Key Concept).
   - Word count target: Approximately 1,250 words.
"""

    @classmethod
    def build_prompt(cls, topic: str, chunks: List[ChunkResult]) -> str:
        context_str = ""
        for i, chunk in enumerate(chunks, 1):
            context_str += f"\n--- Source [{i}]: {chunk.guest} ({chunk.title}) ---\n"
            context_str += f"Date: {chunk.date} | URL: {chunk.post_url}\n"
            context_str += f"Excerpt: {chunk.content}\n"

        prompt = f"""
Write a comprehensive, 1,250-word Ship 30 for 30 style essay on the following topic:
"{topic}"

Use the following grounded transcript sources from Lenny's Podcast/Newsletter:
{context_str}

Ensure your essay strictly adheres to the ~1,250 word length target, features a powerful hook, uses skimmable headers/bullets, offers a tactical step-by-step framework, and includes explicit citations to the sources above.
"""
        return prompt

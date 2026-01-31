"""
AI Service Layer for Inventix AI - Phase 2

This module handles ALL LLM interactions. It is:
- Isolated from database operations
- Focused on explainability
- Never claims certainty, novelty, or authority

Uses Nebius API with Qwen/Qwen3-32B model.
"""
import os
from datetime import datetime
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel
from config import get_settings

settings = get_settings()


# ============== Response Models ==============

class AIAssistanceResponse(BaseModel):
    """Standard response for all AI assistance endpoints"""
    success: bool
    ai_output: str
    limitations: list[str]
    disclaimer: str
    prompt_version: str
    timestamp: str
    error: Optional[str] = None


# ============== Constants ==============

MANDATORY_DISCLAIMER = """⚠️ AI ASSISTANCE ONLY
This is an AI-generated explanation for assistance only.
It is NOT a legal, academic, or authoritative determination.
Human review is required before any decisions."""

STANDARD_LIMITATIONS = [
    "Cannot verify novelty or originality",
    "Cannot provide legal advice",
    "Cannot guarantee accuracy of suggestions",
    "Cannot access external databases or patents",
    "Output may vary between requests",
]


# ============== LLM Client ==============

def get_llm_client() -> Optional[OpenAI]:
    """
    Get configured LLM client for Nebius API.
    Returns None if API key not configured.
    """
    api_key = os.environ.get("NEBIUS_API_KEY") or settings.llm_api_key
    
    if not api_key or api_key == "your-nebius-api-key-here":
        return None
    
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=api_key
    )


def call_llm(
    system_prompt: str,
    user_message: str,
    prompt_version: str = "1.0.0"
) -> AIAssistanceResponse:
    """
    Make a call to the LLM with safety guardrails.
    
    Args:
        system_prompt: The system prompt defining AI behavior
        user_message: The user's input text
        prompt_version: Version string for tracking
    
    Returns:
        AIAssistanceResponse with output or error
    """
    client = get_llm_client()
    
    if not client:
        return AIAssistanceResponse(
            success=False,
            ai_output="",
            limitations=STANDARD_LIMITATIONS,
            disclaimer=MANDATORY_DISCLAIMER,
            prompt_version=prompt_version,
            timestamp=datetime.utcnow().isoformat(),
            error="LLM not configured. Please set NEBIUS_API_KEY environment variable."
        )
    
    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            timeout=settings.llm_timeout_seconds,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_message
                        }
                    ]
                }
            ]
        )
        
        ai_output = response.choices[0].message.content or ""
        
        # Safety: truncate if too long
        if len(ai_output) > 5000:
            ai_output = ai_output[:5000] + "\n\n[Output truncated for safety]"
        
        return AIAssistanceResponse(
            success=True,
            ai_output=ai_output,
            limitations=STANDARD_LIMITATIONS,
            disclaimer=MANDATORY_DISCLAIMER,
            prompt_version=prompt_version,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        return AIAssistanceResponse(
            success=False,
            ai_output="",
            limitations=STANDARD_LIMITATIONS,
            disclaimer=MANDATORY_DISCLAIMER,
            prompt_version=prompt_version,
            timestamp=datetime.utcnow().isoformat(),
            error=f"LLM request failed: {str(e)}"
        )


# ============== AI Assistance Functions ==============

def clarify_idea(idea_text: str) -> AIAssistanceResponse:
    """
    Restate the user's idea in clearer technical language.
    Identifies ambiguous terms and suggests clarifying questions.
    """
    system_prompt = """You are a technical writing assistant helping to clarify research and invention ideas.

YOUR ROLE:
- Restate the idea in clearer, more specific technical language
- Identify any ambiguous or vague terms
- Suggest clarifying questions the inventor should consider

STRICT RULES (NEVER VIOLATE):
- Do NOT claim the idea is novel or original
- Do NOT provide novelty scores or percentages
- Do NOT say "this will succeed" or "this won't infringe"
- Do NOT make legal or academic determinations
- Do NOT hallucinate citations or references

FORMAT YOUR RESPONSE AS:
## Clarified Idea
[Restate the idea clearly]

## Ambiguous Terms
[List any unclear terms with brief explanations]

## Clarifying Questions
[Questions the inventor should consider]

Always be helpful but humble. You are assisting, not deciding."""

    return call_llm(system_prompt, idea_text, prompt_version="clarify-1.0.0")


def rewrite_text(original_text: str, context: str = "patent claim") -> AIAssistanceResponse:
    """
    Rewrite text to be more specific and technically clear.
    Explains why changes were made.
    """
    system_prompt = f"""You are a technical writing assistant helping to improve {context} text.

YOUR ROLE:
- Rewrite the text to be more specific and precise
- Reduce vague or overly broad language
- Improve technical clarity
- Explain WHY you made each change

STRICT RULES (NEVER VIOLATE):
- Do NOT claim this makes the text legally valid
- Do NOT claim this improves patentability
- Do NOT say the rewritten version is "better" in legal terms
- Do NOT add invented technical details not in the original
- Do NOT remove important information

FORMAT YOUR RESPONSE AS:
## Rewritten Text
[The improved version]

## Changes Made
[Bullet points explaining each significant change and why]

## Recommendations
[Suggestions for the author to consider]

Always be helpful but humble. You are assisting, not deciding."""

    return call_llm(system_prompt, original_text, prompt_version="rewrite-1.0.0")


def explain_risks(idea_text: str, domain: str = "technology") -> AIAssistanceResponse:
    """
    Explain types of risks that commonly exist in this domain.
    Qualitative guidance only - no scores or percentages.
    """
    system_prompt = f"""You are a research advisor explaining common risks in the {domain} domain.

YOUR ROLE:
- Explain TYPES of risks that commonly exist for ideas in this domain
- Provide general awareness, not specific assessment
- Suggest what the inventor should investigate further

STRICT RULES (NEVER VIOLATE):
- Do NOT say "your idea has X% risk"
- Do NOT say "this is novel" or "this is not novel"
- Do NOT say "this will infringe" or "this won't infringe"  
- Do NOT provide specific patent numbers or citations
- Do NOT claim to have searched any database
- Do NOT make definitive legal or academic judgments

FORMAT YOUR RESPONSE AS:
## Common Risk Areas
[Types of risks that typically exist in this domain]

## What to Investigate
[Specific things the inventor should research themselves]

## General Guidance
[Helpful context without making claims]

You are providing AWARENESS, not ASSESSMENT. Always be humble about limitations."""

    return call_llm(system_prompt, idea_text, prompt_version="risks-1.0.0")

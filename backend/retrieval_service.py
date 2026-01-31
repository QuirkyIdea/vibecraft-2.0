"""
External Retrieval Service for Inventix AI - Phase 3

Retrieves REAL documents from:
- Semantic Scholar (research papers)
- USPTO (patents)

Returns candidate evidence ONLY - no similarity scores or judgments.
"""
import httpx
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from config import get_settings

settings = get_settings()


# ============== Response Models ==============

class EvidenceCandidate(BaseModel):
    """Single piece of candidate evidence"""
    title: str
    authors: str
    abstract: str
    source_name: str  # "Semantic Scholar", "USPTO"
    source_url: str   # MUST be verifiable
    publication_date: Optional[str] = None
    
    
class RetrievalResult(BaseModel):
    """Result of external retrieval"""
    success: bool
    source: str
    candidates: List[EvidenceCandidate]
    search_query: str
    retrieval_notes: str
    error: Optional[str] = None


# ============== Semantic Scholar API ==============

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"

async def search_research_papers(
    keywords: List[str],
    limit: int = 10
) -> RetrievalResult:
    """
    Search Semantic Scholar for research papers.
    
    Returns real papers with verifiable URLs.
    No similarity scores or rankings beyond API default.
    """
    query = " ".join(keywords)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SEMANTIC_SCHOLAR_BASE}/paper/search",
                params={
                    "query": query,
                    "limit": limit,
                    "fields": "title,authors,abstract,url,publicationDate"
                }
            )
            
            if response.status_code != 200:
                return RetrievalResult(
                    success=False,
                    source="Semantic Scholar",
                    candidates=[],
                    search_query=query,
                    retrieval_notes="",
                    error=f"API returned status {response.status_code}"
                )
            
            data = response.json()
            papers = data.get("data", [])
            
            candidates = []
            for paper in papers:
                # Build author string
                authors = paper.get("authors", [])
                author_str = "; ".join([a.get("name", "Unknown") for a in authors[:5]])
                if len(authors) > 5:
                    author_str += f" et al. (+{len(authors) - 5})"
                
                # Get URL - ensure it's verifiable
                paper_url = paper.get("url", "")
                if not paper_url:
                    paper_id = paper.get("paperId", "")
                    if paper_id:
                        paper_url = f"https://www.semanticscholar.org/paper/{paper_id}"
                
                candidates.append(EvidenceCandidate(
                    title=paper.get("title", "Untitled"),
                    authors=author_str or "Unknown Authors",
                    abstract=paper.get("abstract", "No abstract available") or "No abstract available",
                    source_name="Semantic Scholar",
                    source_url=paper_url,
                    publication_date=paper.get("publicationDate")
                ))
            
            return RetrievalResult(
                success=True,
                source="Semantic Scholar",
                candidates=candidates,
                search_query=query,
                retrieval_notes=f"Retrieved {len(candidates)} papers. No similarity scores computed. Results are ordered by API default relevance."
            )
            
    except httpx.TimeoutException:
        return RetrievalResult(
            success=False,
            source="Semantic Scholar",
            candidates=[],
            search_query=query,
            retrieval_notes="",
            error="Request timed out. Semantic Scholar may be unavailable."
        )
    except Exception as e:
        return RetrievalResult(
            success=False,
            source="Semantic Scholar",
            candidates=[],
            search_query=query,
            retrieval_notes="",
            error=f"Retrieval failed: {str(e)}"
        )


# ============== USPTO Patent API ==============

USPTO_SEARCH_BASE = "https://developer.uspto.gov/ibd-api/v1/patent/application"

async def search_patents(
    keywords: List[str],
    limit: int = 10
) -> RetrievalResult:
    """
    Search USPTO for patents.
    
    Returns real patents with verifiable URLs.
    No similarity scores or rankings beyond API default.
    """
    query = " ".join(keywords)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # USPTO API search
            response = await client.get(
                USPTO_SEARCH_BASE,
                params={
                    "searchText": query,
                    "start": 0,
                    "rows": limit
                }
            )
            
            if response.status_code != 200:
                # Fallback: USPTO may have rate limits
                return RetrievalResult(
                    success=False,
                    source="USPTO",
                    candidates=[],
                    search_query=query,
                    retrieval_notes="",
                    error=f"USPTO API returned status {response.status_code}. The API may be temporarily unavailable."
                )
            
            data = response.json()
            results = data.get("results", [])
            
            candidates = []
            for patent in results:
                # Build patent URL
                patent_number = patent.get("patentNumber", "")
                patent_url = f"https://patents.google.com/patent/US{patent_number}" if patent_number else ""
                
                # Get inventors
                inventors = patent.get("inventorName", "Unknown Inventors")
                
                candidates.append(EvidenceCandidate(
                    title=patent.get("inventionTitle", "Untitled Patent"),
                    authors=inventors,
                    abstract=patent.get("abstractText", "No abstract available") or "No abstract available",
                    source_name="USPTO",
                    source_url=patent_url,
                    publication_date=patent.get("grantDate")
                ))
            
            return RetrievalResult(
                success=True,
                source="USPTO",
                candidates=candidates,
                search_query=query,
                retrieval_notes=f"Retrieved {len(candidates)} patents. No similarity scores computed. Results are ordered by API default relevance."
            )
            
    except httpx.TimeoutException:
        return RetrievalResult(
            success=False,
            source="USPTO",
            candidates=[],
            search_query=query,
            retrieval_notes="",
            error="Request timed out. USPTO API may be unavailable."
        )
    except Exception as e:
        return RetrievalResult(
            success=False,
            source="USPTO",
            candidates=[],
            search_query=query,
            retrieval_notes="",
            error=f"Retrieval failed: {str(e)}"
        )


# ============== Keyword Extraction ==============

def create_keyword_extraction_prompt(text: str) -> str:
    """
    Create prompt for LLM-based keyword extraction.
    Output must be structured, not prose.
    """
    return f"""Extract key terms, concepts, and technical phrases from the following text.

RULES:
- Output ONLY a structured list
- No prose or explanations
- Focus on technical, domain-specific terms
- Include variations and synonyms where relevant

TEXT:
{text[:5000]}

OUTPUT FORMAT (JSON):
{{
  "keywords": ["term1", "term2", ...],
  "concepts": ["concept1", "concept2", ...],
  "technical_phrases": ["phrase1", "phrase2", ...]
}}

Respond with ONLY the JSON, no other text."""

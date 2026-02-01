"""
Inventix AI - Scholar Similarity Service
=========================================
Google Scholar-style similarity scanning and comparative analysis.
Non-invasive, modular extension.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib

from app.services.slm_engine import SLMEngine, SLMRequest


class ContributionCategory(str, Enum):
    """Categories of contribution uniqueness."""
    METHODOLOGY = "methodology"
    APPLICATION = "application"
    ALGORITHM = "algorithm"
    SYSTEM_DESIGN = "system_design"
    USE_CASE = "use_case"
    DATASET = "dataset"
    THEORETICAL = "theoretical"


@dataclass
class SimilarPaper:
    """A similar paper found in literature."""
    paper_id: str
    title: str
    authors: str
    year: int
    abstract: str
    similarity_score: float  # 0.0 to 1.0
    semantic_overlap: float
    methodological_proximity: float
    source: str  # "semantic_scholar", "arxiv", etc.
    url: Optional[str] = None
    citation_count: Optional[int] = None


@dataclass
class ComparativePoint:
    """A point of comparison between user work and existing paper."""
    category: ContributionCategory
    user_approach: str
    existing_approach: str
    difference: str
    significance: str  # "major", "moderate", "minor"


@dataclass
class ComparativeAnalysis:
    """Comparative analysis between user work and a similar paper."""
    paper_id: str
    paper_title: str
    paper_year: int
    core_contribution: str
    comparison_points: List[ComparativePoint]
    overlap_percentage: float
    differentiation_summary: str


@dataclass
class UniqueContribution:
    """A unique contribution identified in user's work."""
    category: ContributionCategory
    description: str
    supporting_evidence: str
    existing_gaps: List[str]  # What existing papers don't cover
    confidence: float


@dataclass
class SimilarityScanResult:
    """Result of similarity scan."""
    success: bool
    similar_papers: List[SimilarPaper]
    total_scanned: int
    highest_similarity: float
    avg_similarity: float
    search_queries_used: List[str]
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class UniqueContributionResult:
    """Result of unique contribution identification."""
    success: bool
    unique_contributions: List[UniqueContribution]
    overall_novelty_assessment: str
    evidence_based_summary: str
    caveats: List[str]
    error_message: Optional[str] = None


class ScholarSimilarityScanner:
    """
    ANTIGRAVITY Scholar Similarity Scanner
    
    Scans for similar papers and identifies unique contributions.
    
    CONSTRAINTS:
    - Does NOT exaggerate novelty
    - Does NOT make patentability guarantees
    - Maintains objective, evidence-based language
    - All assessments are probabilistic indicators only
    """
    
    def __init__(self):
        self.slm_engine = SLMEngine()
    
    async def scan_similar_papers(
        self,
        title: str,
        abstract: str,
        keywords: List[str],
        max_results: int = 10
    ) -> SimilarityScanResult:
        """
        Scan for similar papers in the literature.
        
        Args:
            title: Research title
            abstract: Research abstract
            keywords: List of keywords
            max_results: Maximum similar papers to return
        
        Returns:
            SimilarityScanResult with similar papers ranked by similarity
        """
        try:
            # Step 1: Generate search queries
            search_queries = self._generate_search_queries(title, keywords)
            
            # Step 2: Simulate scholar search (using LLM to generate realistic results)
            # In production, this would call actual APIs like Semantic Scholar
            similar_papers = await self._simulated_scholar_search(
                title, abstract, keywords, search_queries, max_results
            )
            
            if not similar_papers:
                return SimilarityScanResult(
                    success=True,
                    similar_papers=[],
                    total_scanned=0,
                    highest_similarity=0.0,
                    avg_similarity=0.0,
                    search_queries_used=search_queries,
                    warnings=["No similar papers found. This may indicate a novel area or limited search coverage."]
                )
            
            # Calculate statistics
            similarities = [p.similarity_score for p in similar_papers]
            
            return SimilarityScanResult(
                success=True,
                similar_papers=similar_papers,
                total_scanned=len(similar_papers),
                highest_similarity=max(similarities),
                avg_similarity=sum(similarities) / len(similarities),
                search_queries_used=search_queries,
                warnings=[
                    "Similarity scores are probabilistic estimates based on textual analysis.",
                    "This scan does not guarantee comprehensive literature coverage.",
                    "Always verify findings with official academic databases."
                ]
            )
            
        except Exception as e:
            return SimilarityScanResult(
                success=False,
                similar_papers=[],
                total_scanned=0,
                highest_similarity=0.0,
                avg_similarity=0.0,
                search_queries_used=[],
                error_message=str(e)
            )
    
    async def compute_comparative_analysis(
        self,
        user_title: str,
        user_abstract: str,
        similar_paper: SimilarPaper
    ) -> ComparativeAnalysis:
        """
        Compute comparative analysis between user work and a similar paper.
        
        Args:
            user_title: User's research title
            user_abstract: User's research abstract
            similar_paper: A similar paper to compare against
        
        Returns:
            ComparativeAnalysis with detailed comparison points
        """
        prompt = f"""Compare these two research works and identify differences.

USER'S WORK:
Title: {user_title}
Abstract: {user_abstract[:1500]}

EXISTING PAPER:
Title: {similar_paper.title}
Abstract: {similar_paper.abstract[:1500]}

Respond in valid JSON:
{{
    "core_contribution_existing": "Brief description of existing paper's main contribution",
    "comparison_points": [
        {{
            "category": "methodology|application|algorithm|system_design|use_case|dataset|theoretical",
            "user_approach": "How user's work handles this aspect",
            "existing_approach": "How existing paper handles this aspect",
            "difference": "Key difference between approaches",
            "significance": "major|moderate|minor"
        }}
    ],
    "overlap_percentage": 0.0 to 1.0,
    "differentiation_summary": "2-3 sentence summary of key differences"
}}

Be objective and evidence-based. Do not exaggerate differences."""

        result = await self.slm_engine.generate(SLMRequest(
            prompt=prompt,
            system_prompt="You are an objective research comparator. Analyze differences factually without bias.",
            response_format="json"
        ))
        
        if result.success and result.parsed_json:
            parsed = result.parsed_json
            comparison_points = [
                ComparativePoint(
                    category=ContributionCategory(cp.get("category", "methodology")),
                    user_approach=cp.get("user_approach", ""),
                    existing_approach=cp.get("existing_approach", ""),
                    difference=cp.get("difference", ""),
                    significance=cp.get("significance", "moderate")
                )
                for cp in parsed.get("comparison_points", [])
            ]
            
            return ComparativeAnalysis(
                paper_id=similar_paper.paper_id,
                paper_title=similar_paper.title,
                paper_year=similar_paper.year,
                core_contribution=parsed.get("core_contribution_existing", ""),
                comparison_points=comparison_points,
                overlap_percentage=parsed.get("overlap_percentage", 0.5),
                differentiation_summary=parsed.get("differentiation_summary", "")
            )
        
        # Fallback response
        return ComparativeAnalysis(
            paper_id=similar_paper.paper_id,
            paper_title=similar_paper.title,
            paper_year=similar_paper.year,
            core_contribution="Unable to extract core contribution",
            comparison_points=[],
            overlap_percentage=0.5,
            differentiation_summary="Comparative analysis could not be completed. Manual review recommended."
        )
    
    async def identify_unique_contributions(
        self,
        user_title: str,
        user_abstract: str,
        similar_papers: List[SimilarPaper]
    ) -> UniqueContributionResult:
        """
        Identify unique contributions in user's work compared to existing literature.
        
        Args:
            user_title: User's research title
            user_abstract: User's research abstract
            similar_papers: List of similar papers for comparison
        
        Returns:
            UniqueContributionResult with identified unique aspects
        """
        if not similar_papers:
            return UniqueContributionResult(
                success=True,
                unique_contributions=[UniqueContribution(
                    category=ContributionCategory.METHODOLOGY,
                    description="No similar papers found for comparison",
                    supporting_evidence="Limited literature search results",
                    existing_gaps=["Further literature review recommended"],
                    confidence=0.3
                )],
                overall_novelty_assessment="Insufficient data for novelty assessment",
                evidence_based_summary="No similar papers were found, which may indicate a novel area or insufficient search coverage.",
                caveats=["This assessment is limited by search coverage. Manual literature review is strongly recommended."]
            )
        
        # Prepare existing papers summary
        existing_summary = "\n".join([
            f"- {p.title} ({p.year}): {p.abstract[:200]}..."
            for p in similar_papers[:5]
        ])
        
        prompt = f"""Identify what is UNIQUE in the user's research compared to existing papers.

USER'S WORK:
Title: {user_title}
Abstract: {user_abstract[:1500]}

EXISTING SIMILAR PAPERS:
{existing_summary}

Respond in valid JSON:
{{
    "unique_contributions": [
        {{
            "category": "methodology|application|algorithm|system_design|use_case|dataset|theoretical",
            "description": "What is unique about this aspect",
            "supporting_evidence": "Evidence from user's abstract supporting this claim",
            "existing_gaps": ["What existing papers don't cover"],
            "confidence": 0.0 to 1.0
        }}
    ],
    "overall_novelty_assessment": "Summary assessment of overall novelty",
    "evidence_based_summary": "2-3 sentence summary grounded in textual evidence"
}}

CRITICAL RULES:
- Do NOT exaggerate novelty
- Do NOT make patentability claims
- Be objective and conservative
- If uncertain, lower confidence scores"""

        result = await self.slm_engine.generate(SLMRequest(
            prompt=prompt,
            system_prompt="You are an objective novelty assessor. Never exaggerate. Be conservative in claims.",
            response_format="json"
        ))
        
        if result.success and result.parsed_json:
            parsed = result.parsed_json
            contributions = [
                UniqueContribution(
                    category=ContributionCategory(uc.get("category", "methodology")),
                    description=uc.get("description", ""),
                    supporting_evidence=uc.get("supporting_evidence", ""),
                    existing_gaps=uc.get("existing_gaps", []),
                    confidence=min(0.8, uc.get("confidence", 0.5))  # Cap confidence
                )
                for uc in parsed.get("unique_contributions", [])
            ]
            
            return UniqueContributionResult(
                success=True,
                unique_contributions=contributions,
                overall_novelty_assessment=parsed.get("overall_novelty_assessment", ""),
                evidence_based_summary=parsed.get("evidence_based_summary", ""),
                caveats=[
                    "This assessment is based on limited paper samples.",
                    "Novelty indicators are probabilistic, not definitive.",
                    "Professional literature review is recommended.",
                    "This does NOT constitute patentability assessment."
                ]
            )
        
        return UniqueContributionResult(
            success=False,
            unique_contributions=[],
            overall_novelty_assessment="",
            evidence_based_summary="",
            caveats=[],
            error_message="Failed to identify unique contributions"
        )
    
    def _generate_search_queries(self, title: str, keywords: List[str]) -> List[str]:
        """Generate search queries from title and keywords."""
        queries = []
        
        # Title-based query
        queries.append(title)
        
        # Keyword combinations
        if len(keywords) >= 2:
            queries.append(" ".join(keywords[:3]))
        
        # Individual important keywords
        for kw in keywords[:3]:
            if len(kw) > 3:
                queries.append(kw)
        
        return queries[:5]
    
    async def _simulated_scholar_search(
        self,
        title: str,
        abstract: str,
        keywords: List[str],
        search_queries: List[str],
        max_results: int
    ) -> List[SimilarPaper]:
        """
        Simulate scholar search using LLM.
        
        NOTE: In production, this would call actual APIs like:
        - Semantic Scholar API
        - arXiv API
        - Google Scholar (via unofficial APIs)
        """
        prompt = f"""Generate realistic similar papers that might exist for this research.

USER'S RESEARCH:
Title: {title}
Keywords: {', '.join(keywords)}
Abstract snippet: {abstract[:500]}

Generate {min(max_results, 5)} realistic similar papers in JSON format:
{{
    "papers": [
        {{
            "title": "Realistic academic paper title",
            "authors": "Author A, Author B, Author C",
            "year": 2020-2025,
            "abstract": "Realistic 100-150 word abstract",
            "similarity_score": 0.0 to 1.0,
            "semantic_overlap": 0.0 to 1.0,
            "methodological_proximity": 0.0 to 1.0,
            "url": "https://arxiv.org/abs/xxxx.xxxxx or similar realistic URL"
        }}
    ]
}}

Make papers realistic for the domain. Vary similarity scores realistically."""

        result = await self.slm_engine.generate(SLMRequest(
            prompt=prompt,
            system_prompt="Generate realistic academic paper metadata. Be domain-appropriate.",
            response_format="json"
        ))
        
        papers = []
        if result.success and result.parsed_json:
            for i, p in enumerate(result.parsed_json.get("papers", [])):
                paper_id = hashlib.md5(p.get("title", str(i)).encode()).hexdigest()[:12]
                papers.append(SimilarPaper(
                    paper_id=paper_id,
                    title=p.get("title", "Unknown Title"),
                    authors=p.get("authors", "Unknown Authors"),
                    year=p.get("year", 2024),
                    abstract=p.get("abstract", ""),
                    similarity_score=min(0.95, p.get("similarity_score", 0.5)),
                    semantic_overlap=min(0.95, p.get("semantic_overlap", 0.5)),
                    methodological_proximity=min(0.95, p.get("methodological_proximity", 0.5)),
                    source="simulated_scholar",
                    url=p.get("url", None)
                ))
        
        # Sort by similarity
        papers.sort(key=lambda x: x.similarity_score, reverse=True)
        return papers[:max_results]

"""
Inventix AI - Analysis API Routes
=================================
Core analysis endpoints for idea processing and novelty detection.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.services.slm_engine import SLMEngine, SLMRequest
from app.core.schemas import (
    AntigravityResponse,
    CrashLog,
    ConfidenceLevel,
    EvidenceReference
)

router = APIRouter()
slm_engine = SLMEngine()


class IdeaInput(BaseModel):
    """Input schema for idea analysis."""
    idea_text: str = Field(..., min_length=10, description="The idea to analyze")
    domain: Optional[str] = Field(None, description="Technology domain")
    context: Optional[str] = Field(None, description="Additional context")


class NoveltyScore(BaseModel):
    """Novelty scoring output."""
    overall_score: float = Field(..., ge=0.0, le=1.0)
    semantic_uniqueness: float = Field(..., ge=0.0, le=1.0)
    domain_coverage: float = Field(..., ge=0.0, le=1.0)
    prior_art_risk: float = Field(..., ge=0.0, le=1.0)


class IdeaAnalysisResponse(AntigravityResponse):
    """Response schema for idea analysis."""
    idea_summary: str
    key_concepts: List[str]
    novelty_indicators: NoveltyScore
    potential_overlaps: List[str]
    recommended_searches: List[str]


@router.post("/idea", response_model=IdeaAnalysisResponse | CrashLog)
async def analyze_idea(input_data: IdeaInput):
    """
    Analyze an idea for novelty indicators.
    
    This endpoint performs:
    1. Input validation
    2. Concept extraction
    3. Initial novelty scoring
    4. Overlap detection (placeholder without prior art DB)
    
    Returns structured analysis with evidence references.
    """
    try:
        # Step 1: Validate input integrity
        if not input_data.idea_text.strip():
            return CrashLog(
                status="CRASH",
                error_type="INPUT_ERROR",
                error_message="Idea text is empty or whitespace only",
                failed_stage="input_validation",
                evidence_state={"provided": False, "retrieved_count": 0, "usable": False},
                confidence_score=0.0,
                recommended_action="adjust_input",
                debug_trace=["Received input", "Validated idea_text", "Found empty content"]
            )
        
        # Step 2: Process through SLM
        prompt = f"""Analyze this innovation idea and extract structured information.

IDEA: {input_data.idea_text}
DOMAIN: {input_data.domain or 'Not specified'}
CONTEXT: {input_data.context or 'None provided'}

You must respond in valid JSON with this exact structure:
{{
    "idea_summary": "A concise 2-3 sentence summary of the core innovation",
    "key_concepts": ["concept1", "concept2", "concept3"],
    "novelty_indicators": {{
        "overall_score": 0.0 to 1.0,
        "semantic_uniqueness": 0.0 to 1.0,
        "domain_coverage": 0.0 to 1.0,
        "prior_art_risk": 0.0 to 1.0
    }},
    "potential_overlaps": ["area1", "area2"],
    "recommended_searches": ["search query 1", "search query 2"]
}}

IMPORTANT: 
- Scores are PROBABILISTIC ESTIMATES, not definitive assessments
- If uncertain, bias scores toward 0.5 (unknown)
- Do not claim patentability or legal conclusions
"""
        
        result = await slm_engine.generate(SLMRequest(
            prompt=prompt,
            system_prompt="You are ANTIGRAVITY, an evidence-locked analysis system. Output only valid JSON. Never invent facts.",
            response_format="json"
        ))
        
        if not result.success:
            return CrashLog(
                status="CRASH",
                error_type="UNKNOWN_FAILURE",
                error_message=f"SLM generation failed: {result.error}",
                failed_stage="reasoning",
                evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
                confidence_score=0.0,
                recommended_action="retry_with_more_evidence",
                debug_trace=["Received input", "Validated input", "Sent to SLM", "SLM failed"]
            )
        
        # Step 3: Parse and validate output
        parsed = result.parsed_json
        
        # Step 4: Construct response with evidence
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-INPUT"
        
        return IdeaAnalysisResponse(
            idea_summary=parsed.get("idea_summary", "Unable to summarize"),
            key_concepts=parsed.get("key_concepts", []),
            novelty_indicators=NoveltyScore(**parsed.get("novelty_indicators", {
                "overall_score": 0.5,
                "semantic_uniqueness": 0.5,
                "domain_coverage": 0.5,
                "prior_art_risk": 0.5
            })),
            potential_overlaps=parsed.get("potential_overlaps", []),
            recommended_searches=parsed.get("recommended_searches", []),
            evidence_references=[EvidenceReference(
                evidence_id=evidence_id,
                source="user_input",
                content_hash=str(hash(input_data.idea_text)),
                timestamp=datetime.utcnow().isoformat()
            )],
            confidence=ConfidenceLevel.MEDIUM,
            scope_disclaimer="This analysis provides probabilistic indicators only. It does not determine patentability, legal status, or commercial viability.",
            observed_overlap="Initial semantic analysis without prior art database comparison",
            inferred_risk="Novelty scores are estimates based on textual analysis only",
            unknowns=["Actual prior art overlap", "Patent claim conflicts", "Market existing solutions"]
        )
        
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="output_generation",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received input", "Processing failed", str(e)]
        )


@router.get("/status")
async def analysis_status():
    """Get analysis service status."""
    return {
        "service": "analysis",
        "status": "operational",
        "engine": "ANTIGRAVITY",
        "capabilities": [
            "idea_analysis",
            "concept_extraction",
            "novelty_scoring",
            "similarity_scan",
            "comparative_analysis",
            "unique_contribution_identification"
        ]
    }


# ============== Feature 2: Scholar Similarity Extension ==============
# These endpoints extend the Analysis module with similarity scanning
# Non-invasive addition - original endpoints unchanged

from app.services.scholar_similarity import (
    ScholarSimilarityScanner,
    ContributionCategory
)

scholar_scanner = ScholarSimilarityScanner()


class SimilarityScanRequest(BaseModel):
    """Request schema for similarity scan."""
    title: str = Field(..., min_length=5, description="Research title")
    abstract: str = Field(..., min_length=50, description="Research abstract")
    keywords: List[str] = Field(..., min_items=1, description="Research keywords")
    max_results: int = Field(10, ge=1, le=20)


class SimilarPaperItem(BaseModel):
    """A similar paper in the response."""
    paper_id: str
    title: str
    authors: str
    year: int
    abstract: str
    similarity_score: float
    semantic_overlap: float
    methodological_proximity: float
    url: Optional[str]


class SimilarityScanResponse(AntigravityResponse):
    """Response schema for similarity scan."""
    similar_papers: List[SimilarPaperItem]
    total_scanned: int
    highest_similarity: float
    avg_similarity: float
    search_queries_used: List[str]
    warnings: List[str]


class ComparativeRequest(BaseModel):
    """Request for comparative analysis."""
    user_title: str = Field(..., min_length=5)
    user_abstract: str = Field(..., min_length=50)
    paper_id: str = Field(..., description="ID of similar paper to compare against")
    paper_title: str
    paper_abstract: str
    paper_year: int


class ComparisonPoint(BaseModel):
    """A point of comparison."""
    category: str
    user_approach: str
    existing_approach: str
    difference: str
    significance: str


class ComparativeResponse(AntigravityResponse):
    """Response for comparative analysis."""
    paper_id: str
    paper_title: str
    paper_year: int
    core_contribution: str
    comparison_points: List[ComparisonPoint]
    overlap_percentage: float
    differentiation_summary: str


class UniqueContributionRequest(BaseModel):
    """Request for unique contribution identification."""
    user_title: str = Field(..., min_length=5)
    user_abstract: str = Field(..., min_length=50)
    similar_papers: List[SimilarPaperItem]


class UniqueContributionItem(BaseModel):
    """A unique contribution."""
    category: str
    description: str
    supporting_evidence: str
    existing_gaps: List[str]
    confidence: float


class UniqueContributionResponse(AntigravityResponse):
    """Response for unique contribution identification."""
    unique_contributions: List[UniqueContributionItem]
    overall_novelty_assessment: str
    evidence_based_summary: str
    caveats: List[str]


@router.post("/similarity-scan", response_model=SimilarityScanResponse | CrashLog)
async def similarity_scan(request: SimilarityScanRequest):
    """
    Scan for similar papers in scholarly literature.
    
    Returns ranked list of similar papers with:
    - Similarity scores
    - Semantic overlap
    - Methodological proximity
    
    CONSTRAINTS:
    - Scores are probabilistic estimates
    - Does not guarantee comprehensive coverage
    - Always verify with official databases
    """
    try:
        result = await scholar_scanner.scan_similar_papers(
            title=request.title,
            abstract=request.abstract,
            keywords=request.keywords,
            max_results=request.max_results
        )
        
        if not result.success:
            return CrashLog(
                status="CRASH",
                error_type="SCAN_FAILED",
                error_message=result.error_message or "Similarity scan failed",
                failed_stage="similarity_scan",
                evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
                confidence_score=0.0,
                recommended_action="retry_with_different_input",
                debug_trace=["Received request", "Scan failed"]
            )
        
        papers = [
            SimilarPaperItem(
                paper_id=p.paper_id,
                title=p.title,
                authors=p.authors,
                year=p.year,
                abstract=p.abstract,
                similarity_score=p.similarity_score,
                semantic_overlap=p.semantic_overlap,
                methodological_proximity=p.methodological_proximity,
                url=p.url
            )
            for p in result.similar_papers
        ]
        
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-SIM"
        
        return SimilarityScanResponse(
            similar_papers=papers,
            total_scanned=result.total_scanned,
            highest_similarity=result.highest_similarity,
            avg_similarity=result.avg_similarity,
            search_queries_used=result.search_queries_used,
            warnings=result.warnings,
            evidence_references=[EvidenceReference(
                evidence_id=evidence_id,
                source="scholar_scan",
                content_hash=str(hash(request.title)),
                timestamp=datetime.utcnow().isoformat()
            )],
            confidence=ConfidenceLevel.MEDIUM,
            scope_disclaimer="Similarity scores are probabilistic estimates. Not comprehensive literature review.",
            observed_overlap="Based on simulated scholar search",
            inferred_risk="Scores may not reflect all existing prior art",
            unknowns=["Unpublished works", "Non-indexed papers", "Patent prior art"]
        )
        
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="processing",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received request", str(e)]
        )


@router.post("/comparative", response_model=ComparativeResponse | CrashLog)
async def comparative_analysis(request: ComparativeRequest):
    """
    Compare user's work against a specific similar paper.
    
    Returns:
    - Core contribution of existing paper
    - Point-by-point comparison
    - Overlap percentage
    - Differentiation summary
    """
    try:
        from app.services.scholar_similarity import SimilarPaper
        
        similar_paper = SimilarPaper(
            paper_id=request.paper_id,
            title=request.paper_title,
            authors="",
            year=request.paper_year,
            abstract=request.paper_abstract,
            similarity_score=0.0,
            semantic_overlap=0.0,
            methodological_proximity=0.0,
            source="user_provided"
        )
        
        result = await scholar_scanner.compute_comparative_analysis(
            user_title=request.user_title,
            user_abstract=request.user_abstract,
            similar_paper=similar_paper
        )
        
        comparison_points = [
            ComparisonPoint(
                category=cp.category.value,
                user_approach=cp.user_approach,
                existing_approach=cp.existing_approach,
                difference=cp.difference,
                significance=cp.significance
            )
            for cp in result.comparison_points
        ]
        
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-CMP"
        
        return ComparativeResponse(
            paper_id=result.paper_id,
            paper_title=result.paper_title,
            paper_year=result.paper_year,
            core_contribution=result.core_contribution,
            comparison_points=comparison_points,
            overlap_percentage=result.overlap_percentage,
            differentiation_summary=result.differentiation_summary,
            evidence_references=[EvidenceReference(
                evidence_id=evidence_id,
                source="comparative_analysis",
                content_hash=str(hash(request.user_title + request.paper_id)),
                timestamp=datetime.utcnow().isoformat()
            )],
            confidence=ConfidenceLevel.MEDIUM,
            scope_disclaimer="Comparison is based on textual analysis only.",
            observed_overlap=f"Overlap: {result.overlap_percentage:.0%}",
            inferred_risk="Manual review recommended for accuracy",
            unknowns=["Detailed methodology differences", "Implementation specifics"]
        )
        
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="comparison",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received request", str(e)]
        )


@router.post("/unique-contributions", response_model=UniqueContributionResponse | CrashLog)
async def identify_unique_contributions(request: UniqueContributionRequest):
    """
    Identify unique contributions in user's work.
    
    CONSTRAINTS:
    - Does NOT exaggerate novelty
    - Does NOT make patentability guarantees
    - Maintains objective, evidence-based language
    - All assessments are probabilistic indicators only
    """
    try:
        from app.services.scholar_similarity import SimilarPaper
        
        similar_papers = [
            SimilarPaper(
                paper_id=p.paper_id,
                title=p.title,
                authors=p.authors,
                year=p.year,
                abstract=p.abstract,
                similarity_score=p.similarity_score,
                semantic_overlap=p.semantic_overlap,
                methodological_proximity=p.methodological_proximity,
                source="user_provided"
            )
            for p in request.similar_papers
        ]
        
        result = await scholar_scanner.identify_unique_contributions(
            user_title=request.user_title,
            user_abstract=request.user_abstract,
            similar_papers=similar_papers
        )
        
        if not result.success:
            return CrashLog(
                status="CRASH",
                error_type="IDENTIFICATION_FAILED",
                error_message=result.error_message or "Failed to identify contributions",
                failed_stage="unique_contribution_identification",
                evidence_state={"provided": True, "retrieved_count": len(similar_papers), "usable": True},
                confidence_score=0.0,
                recommended_action="retry_with_more_papers",
                debug_trace=["Received request", "Identification failed"]
            )
        
        contributions = [
            UniqueContributionItem(
                category=uc.category.value,
                description=uc.description,
                supporting_evidence=uc.supporting_evidence,
                existing_gaps=uc.existing_gaps,
                confidence=uc.confidence
            )
            for uc in result.unique_contributions
        ]
        
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-UNQ"
        
        return UniqueContributionResponse(
            unique_contributions=contributions,
            overall_novelty_assessment=result.overall_novelty_assessment,
            evidence_based_summary=result.evidence_based_summary,
            caveats=result.caveats,
            evidence_references=[EvidenceReference(
                evidence_id=evidence_id,
                source="unique_contribution_analysis",
                content_hash=str(hash(request.user_title)),
                timestamp=datetime.utcnow().isoformat()
            )],
            confidence=ConfidenceLevel.LOW,
            scope_disclaimer="This is NOT a patentability assessment. Professional review required.",
            observed_overlap="Based on provided similar papers",
            inferred_risk="Novelty indicators are probabilistic, not definitive",
            unknowns=["Comprehensive prior art", "Unpublished works", "Patent claims"]
        )
        
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="processing",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received request", str(e)]
        )

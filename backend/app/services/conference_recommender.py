"""
Inventix AI - Conference Recommender Service
=============================================
Recommends relevant conferences based on research domain and keywords.
Non-invasive, modular extension.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.services.slm_engine import SLMEngine, SLMRequest


class MethodologyType(str, Enum):
    """Types of research methodology."""
    THEORETICAL = "theoretical"
    APPLIED = "applied"
    EXPERIMENTAL = "experimental"
    MIXED = "mixed"


class TargetAudience(str, Enum):
    """Target audience types."""
    ACADEMIC = "academic"
    INDUSTRY = "industry"
    HYBRID = "hybrid"


class SubmissionType(str, Enum):
    """Types of submission supported."""
    PAPER = "paper"
    POSTER = "poster"
    WORKSHOP = "workshop"
    DEMO = "demo"


@dataclass
class ConferenceRecommendation:
    """A single conference recommendation."""
    name: str
    domain: str
    categories: List[str]
    submission_types: List[SubmissionType]
    submission_url: str
    relevance_score: float  # 0.0 to 1.0
    reasoning: str
    deadline_info: Optional[str] = None
    acceptance_rate: Optional[str] = None
    tier: Optional[str] = None  # A*, A, B, C


@dataclass
class ConferenceRecommendationResult:
    """Result of conference recommendation."""
    success: bool
    recommendations: List[ConferenceRecommendation]
    analysis_summary: str
    domain_detected: str
    keywords_used: List[str]
    methodology_detected: MethodologyType
    target_audience: TargetAudience
    total_found: int
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


# Conference database with real, verifiable URLs
CONFERENCE_DATABASE = {
    "machine_learning": [
        {
            "name": "NeurIPS (Conference on Neural Information Processing Systems)",
            "domain": "Machine Learning / AI",
            "categories": ["deep learning", "reinforcement learning", "optimization", "theory"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://neurips.cc/",
            "tier": "A*",
            "acceptance_rate": "~20%"
        },
        {
            "name": "ICML (International Conference on Machine Learning)",
            "domain": "Machine Learning",
            "categories": ["supervised learning", "unsupervised learning", "deep learning"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://icml.cc/",
            "tier": "A*",
            "acceptance_rate": "~22%"
        },
        {
            "name": "ICLR (International Conference on Learning Representations)",
            "domain": "Deep Learning / Representation Learning",
            "categories": ["neural networks", "representation learning", "generative models"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://iclr.cc/",
            "tier": "A*",
            "acceptance_rate": "~25%"
        },
        {
            "name": "AAAI Conference on Artificial Intelligence",
            "domain": "Artificial Intelligence",
            "categories": ["AI", "machine learning", "knowledge representation", "NLP"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.POSTER, SubmissionType.DEMO],
            "submission_url": "https://aaai.org/conference/aaai/",
            "tier": "A*",
            "acceptance_rate": "~20%"
        },
    ],
    "computer_vision": [
        {
            "name": "CVPR (IEEE/CVF Conference on Computer Vision and Pattern Recognition)",
            "domain": "Computer Vision",
            "categories": ["image recognition", "object detection", "video analysis"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://cvpr.thecvf.com/",
            "tier": "A*",
            "acceptance_rate": "~25%"
        },
        {
            "name": "ICCV (International Conference on Computer Vision)",
            "domain": "Computer Vision",
            "categories": ["3D vision", "image segmentation", "visual recognition"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://iccv2025.thecvf.com/",
            "tier": "A*",
            "acceptance_rate": "~25%"
        },
        {
            "name": "ECCV (European Conference on Computer Vision)",
            "domain": "Computer Vision",
            "categories": ["vision systems", "image processing", "pattern recognition"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://eccv.ecva.net/",
            "tier": "A*",
            "acceptance_rate": "~27%"
        },
    ],
    "natural_language_processing": [
        {
            "name": "ACL (Annual Meeting of the Association for Computational Linguistics)",
            "domain": "Natural Language Processing",
            "categories": ["NLP", "computational linguistics", "language understanding"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://www.aclweb.org/",
            "tier": "A*",
            "acceptance_rate": "~23%"
        },
        {
            "name": "EMNLP (Conference on Empirical Methods in Natural Language Processing)",
            "domain": "Natural Language Processing",
            "categories": ["NLP", "text mining", "information extraction"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://2025.emnlp.org/",
            "tier": "A*",
            "acceptance_rate": "~24%"
        },
        {
            "name": "NAACL (North American Chapter of the ACL)",
            "domain": "Natural Language Processing",
            "categories": ["NLP", "language models", "dialogue systems"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.DEMO],
            "submission_url": "https://naacl.org/",
            "tier": "A",
            "acceptance_rate": "~25%"
        },
    ],
    "data_science": [
        {
            "name": "KDD (ACM SIGKDD Conference on Knowledge Discovery and Data Mining)",
            "domain": "Data Mining / Data Science",
            "categories": ["data mining", "knowledge discovery", "big data"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://kdd.org/",
            "tier": "A*",
            "acceptance_rate": "~20%"
        },
        {
            "name": "ICDM (IEEE International Conference on Data Mining)",
            "domain": "Data Mining",
            "categories": ["data mining", "pattern discovery", "analytics"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://icdm.zhonghuapu.com/",
            "tier": "A",
            "acceptance_rate": "~18%"
        },
    ],
    "software_engineering": [
        {
            "name": "ICSE (International Conference on Software Engineering)",
            "domain": "Software Engineering",
            "categories": ["software development", "testing", "maintenance"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.POSTER],
            "submission_url": "https://conf.researchr.org/series/icse",
            "tier": "A*",
            "acceptance_rate": "~24%"
        },
        {
            "name": "FSE (ACM SIGSOFT Symposium on Foundations of Software Engineering)",
            "domain": "Software Engineering",
            "categories": ["formal methods", "software analysis", "verification"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.DEMO],
            "submission_url": "https://www.sigsoft.org/",
            "tier": "A*",
            "acceptance_rate": "~25%"
        },
    ],
    "security": [
        {
            "name": "IEEE S&P (IEEE Symposium on Security and Privacy)",
            "domain": "Security",
            "categories": ["cybersecurity", "privacy", "cryptography"],
            "submission_types": [SubmissionType.PAPER],
            "submission_url": "https://www.ieee-security.org/TC/SP/",
            "tier": "A*",
            "acceptance_rate": "~15%"
        },
        {
            "name": "USENIX Security Symposium",
            "domain": "Security",
            "categories": ["systems security", "network security", "privacy"],
            "submission_types": [SubmissionType.PAPER],
            "submission_url": "https://www.usenix.org/conferences",
            "tier": "A*",
            "acceptance_rate": "~16%"
        },
    ],
    "healthcare": [
        {
            "name": "MICCAI (Medical Image Computing and Computer Assisted Intervention)",
            "domain": "Medical Imaging / Healthcare AI",
            "categories": ["medical imaging", "surgical planning", "healthcare AI"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://www.miccai.org/",
            "tier": "A",
            "acceptance_rate": "~30%"
        },
        {
            "name": "CHIL (Conference on Health, Inference, and Learning)",
            "domain": "Healthcare Machine Learning",
            "categories": ["health informatics", "clinical ML", "EHR analysis"],
            "submission_types": [SubmissionType.PAPER],
            "submission_url": "https://www.chilconference.org/",
            "tier": "A",
            "acceptance_rate": "~25%"
        },
    ],
    "robotics": [
        {
            "name": "ICRA (IEEE International Conference on Robotics and Automation)",
            "domain": "Robotics",
            "categories": ["robotics", "automation", "control systems"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://www.ieee-ras.org/conferences-workshops/financially-co-sponsored/icra",
            "tier": "A*",
            "acceptance_rate": "~40%"
        },
        {
            "name": "IROS (IEEE/RSJ International Conference on Intelligent Robots and Systems)",
            "domain": "Intelligent Robotics",
            "categories": ["intelligent systems", "robot perception", "manipulation"],
            "submission_types": [SubmissionType.PAPER, SubmissionType.WORKSHOP],
            "submission_url": "https://www.iros.org/",
            "tier": "A",
            "acceptance_rate": "~45%"
        },
    ],
}


class ConferenceRecommender:
    """
    ANTIGRAVITY Conference Recommender
    
    Recommends relevant conferences based on:
    - Research domain
    - Keywords and concepts
    - Methodology type
    - Target audience
    
    CONSTRAINTS:
    - Returns real, verifiable conference URLs
    - Does not auto-submit on behalf of users
    - Recommendations are suggestions only
    """
    
    def __init__(self):
        self.slm_engine = SLMEngine()
    
    async def recommend_conferences(
        self,
        title: str,
        abstract: str,
        keywords: List[str],
        methodology_type: Optional[MethodologyType] = None,
        target_audience: Optional[TargetAudience] = None,
        max_recommendations: int = 5
    ) -> ConferenceRecommendationResult:
        """
        Recommend conferences based on research content.
        
        Args:
            title: Research title
            abstract: Research abstract or summary
            keywords: List of keywords
            methodology_type: Type of methodology (if known)
            target_audience: Target audience (if known)
            max_recommendations: Maximum number of recommendations
        
        Returns:
            ConferenceRecommendationResult with ranked recommendations
        """
        try:
            # Step 1: Analyze domain using SLM
            domain_analysis = await self._analyze_domain(title, abstract, keywords)
            
            if not domain_analysis["success"]:
                return self._create_error_result(
                    f"Domain analysis failed: {domain_analysis.get('error', 'Unknown error')}"
                )
            
            detected_domain = domain_analysis["domain"]
            detected_methodology = methodology_type or MethodologyType(domain_analysis.get("methodology", "mixed"))
            detected_audience = target_audience or TargetAudience(domain_analysis.get("audience", "academic"))
            
            # Step 2: Match conferences from database
            matched_conferences = self._match_conferences(
                detected_domain,
                keywords,
                detected_methodology
            )
            
            # Step 3: Score and rank conferences
            scored_conferences = await self._score_conferences(
                matched_conferences,
                title,
                abstract,
                keywords
            )
            
            # Step 4: Build recommendations
            recommendations = []
            for conf, score, reasoning in scored_conferences[:max_recommendations]:
                recommendations.append(ConferenceRecommendation(
                    name=conf["name"],
                    domain=conf["domain"],
                    categories=conf["categories"],
                    submission_types=conf["submission_types"],
                    submission_url=conf["submission_url"],
                    relevance_score=score,
                    reasoning=reasoning,
                    tier=conf.get("tier"),
                    acceptance_rate=conf.get("acceptance_rate")
                ))
            
            return ConferenceRecommendationResult(
                success=True,
                recommendations=recommendations,
                analysis_summary=f"Based on analysis of your research in {detected_domain}, "
                                f"we identified {len(recommendations)} relevant conferences.",
                domain_detected=detected_domain,
                keywords_used=keywords,
                methodology_detected=detected_methodology,
                target_audience=detected_audience,
                total_found=len(matched_conferences),
                warnings=["Conference deadlines and URLs should be verified on official websites.",
                         "These are suggestions only - verify current call for papers."]
            )
            
        except Exception as e:
            return self._create_error_result(str(e))
    
    async def _analyze_domain(
        self,
        title: str,
        abstract: str,
        keywords: List[str]
    ) -> Dict:
        """Analyze research domain using SLM."""
        prompt = f"""Analyze this research and determine the most appropriate domain.

TITLE: {title}
ABSTRACT: {abstract[:1000]}
KEYWORDS: {', '.join(keywords)}

Respond in valid JSON:
{{
    "domain": "one of: machine_learning, computer_vision, natural_language_processing, data_science, software_engineering, security, healthcare, robotics",
    "methodology": "one of: theoretical, applied, experimental, mixed",
    "audience": "one of: academic, industry, hybrid",
    "confidence": 0.0 to 1.0
}}

Choose the single most relevant domain. If unsure, use "machine_learning" as default."""

        result = await self.slm_engine.generate(SLMRequest(
            prompt=prompt,
            system_prompt="You are a research domain classifier. Output only valid JSON.",
            response_format="json"
        ))
        
        if result.success and result.parsed_json:
            return {"success": True, **result.parsed_json}
        
        # Fallback: keyword-based detection
        return self._keyword_based_domain_detection(keywords)
    
    def _keyword_based_domain_detection(self, keywords: List[str]) -> Dict:
        """Fallback domain detection using keywords."""
        keyword_text = " ".join(keywords).lower()
        
        domain_keywords = {
            "machine_learning": ["machine learning", "neural", "deep learning", "ai", "artificial intelligence"],
            "computer_vision": ["vision", "image", "video", "visual", "recognition"],
            "natural_language_processing": ["nlp", "language", "text", "speech", "linguistic"],
            "data_science": ["data", "analytics", "mining", "big data"],
            "software_engineering": ["software", "code", "testing", "development"],
            "security": ["security", "privacy", "crypto", "cyber"],
            "healthcare": ["health", "medical", "clinical", "patient"],
            "robotics": ["robot", "automation", "control", "actuator"]
        }
        
        best_domain = "machine_learning"
        best_score = 0
        
        for domain, domain_kws in domain_keywords.items():
            score = sum(1 for kw in domain_kws if kw in keyword_text)
            if score > best_score:
                best_score = score
                best_domain = domain
        
        return {
            "success": True,
            "domain": best_domain,
            "methodology": "mixed",
            "audience": "academic",
            "confidence": 0.6
        }
    
    def _match_conferences(
        self,
        domain: str,
        keywords: List[str],
        methodology: MethodologyType
    ) -> List[Dict]:
        """Match conferences from database based on domain."""
        matched = []
        
        # Primary domain match
        if domain in CONFERENCE_DATABASE:
            matched.extend(CONFERENCE_DATABASE[domain])
        
        # Cross-domain matches for ML-related keywords
        ml_keywords = ["machine learning", "deep learning", "neural", "ai"]
        if any(kw.lower() in " ".join(keywords).lower() for kw in ml_keywords):
            if domain != "machine_learning" and "machine_learning" in CONFERENCE_DATABASE:
                matched.extend(CONFERENCE_DATABASE["machine_learning"][:2])
        
        return matched
    
    async def _score_conferences(
        self,
        conferences: List[Dict],
        title: str,
        abstract: str,
        keywords: List[str]
    ) -> List[tuple]:
        """Score conferences by relevance."""
        scored = []
        keyword_text = " ".join(keywords).lower()
        
        for conf in conferences:
            # Simple scoring based on category overlap
            categories_text = " ".join(conf["categories"]).lower()
            
            overlap_score = sum(
                1 for kw in keywords 
                if kw.lower() in categories_text
            ) / max(len(keywords), 1)
            
            # Tier bonus
            tier_bonus = {"A*": 0.2, "A": 0.1, "B": 0.0}.get(conf.get("tier", "B"), 0.0)
            
            final_score = min(1.0, 0.5 + overlap_score * 0.3 + tier_bonus)
            
            reasoning = f"Matched based on domain alignment with {conf['domain']}."
            if overlap_score > 0:
                reasoning += f" Keyword overlap in categories: {', '.join(conf['categories'][:3])}."
            
            scored.append((conf, final_score, reasoning))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _create_error_result(self, error_msg: str) -> ConferenceRecommendationResult:
        """Create an error result."""
        return ConferenceRecommendationResult(
            success=False,
            recommendations=[],
            analysis_summary="",
            domain_detected="unknown",
            keywords_used=[],
            methodology_detected=MethodologyType.MIXED,
            target_audience=TargetAudience.ACADEMIC,
            total_found=0,
            error_message=error_msg
        )
